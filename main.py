def new_board(rows=3, cols=3):
    return [[' ' for _ in range(cols)] for _ in range(rows)]

def board_to_string(board):
    return ''.join([''.join(row) for row in board])

def string_to_board(board_string, rows=3, cols=3):
    return [list(board_string[i*cols:(1+i)*cols]) for i in range(rows)]

def copy_board(board):
    return string_to_board(board_to_string(board), len(board), len(board[0]))

def flip_board(board, vertically=True): # flips board vertically or horizontally
    if vertically: return board[::-1]
    return [row[::-1] for row in board] # horizontal flip

def diagonal_board(board): # flips board along the diagonal (should only be performed on square boards)
    return list(zip(*board))

def rotate_board(board): # (should only be performed on square boards)
    return diagonal_board(flip_board(board))

def board_symmetries(board, gravity=False):
    board_copy = copy_board(board)
    symmetries = set([board_to_string(board_copy)])
    if gravity:
        board_copy = flip_board(board_copy, vertically=False)
        symmetries.add(board_to_string(board_copy))
    elif len(board) == len(board[0]):
        r, d = rotate_board, diagonal_board
        for z in [r, r, r, d, r, r, r]:
            board_copy = z(board_copy)
            symmetries.add(board_to_string(board_copy))
    else:
        for flip in [True, False, True]:
            board_copy = flip_board(board_copy, vertically=flip)
            symmetries.add(board_to_string(board_copy))
    return symmetries

def check_winner(board, rule=3):
    def sliding_window(array):
        for sub_list in zip(*(array[i:] for i in range(rule))):
            x = sub_list[0]
            if x != " " and sub_list.count(x) == rule:
                return x
    def get_diagonal(board, n, mirror=False):
        rows = len(board)
        cols = len(board[0])
        if mirror:
            board = flip_board(board, vertically=False)
        diag = []
        for i in range(rows):
            j = i + n
            if 0 <= j < cols:
                diag.append(board[i][j])
        return diag
    for row in board:
        if x := sliding_window(row): return x
    for col in rotate_board(board):
        if x := sliding_window(col): return x
    for diag in [get_diagonal(board, n) for n in range(rule - len(board), len(board[0]) - rule + 1)]:
        if x := sliding_window(diag): return x
    for diag in [get_diagonal(board, n, mirror=True) for n in range(rule - len(board), len(board[0]) - rule + 1)]:
        if x := sliding_window(diag): return x
    return "draw" if board_to_string(board).count(" ") == 0 else None

def legal_moves(board, gravity=False):
    cols = len(board[0])
    if gravity:
        return [c for c in range(cols) if board[0][c] == " "]
    rows = len(board)
    return [(r, c) for r in range(rows) for c in range(cols) if board[r][c] == " "]

def apply_move(board, move, player, gravity=False):
    board_copy = copy_board(board)
    if gravity:
        col = [board[row][move] for row in range(len(board))]
        row = len(col) - 1 - col[::-1].index(" ")
        board_copy[row][move] = player
    else:
        i, j = move
        board_copy[i][j] = player
    return board_copy

def draw_board(board, string=False, rows=3, cols=3):
    print()
    for row in copy_board(string_to_board(board, rows, cols) if string else board): print(f'║{"│".join(row)}║')

def draw_moves(board_tree, rows=3, cols=3):
    children = board_tree["children"]
    while len(children):
        child = children[0]
        print()
        draw_board(child["board_state"], string=True, rows=rows, cols=cols)
        children = child["children"]

"""
    TODO: current implementation with using counter_move works, however,
    it may not be appropriate to implement in other games due to:
    • exhaustive search taking forever for complex games with large state trees
    • non-perfect information or non-deterministic games

    TODO: memoize evaluating function by storing game results for each unique board state
"""

def build_board_tree(board, player, rule=3, gravity=False, depth=0, max_depth=9):
    board_string = board_to_string(board)
    node = {
        "board_state": board_string,
        "board_value": "",
        "children": []
    }

    winner = check_winner(board, rule)
    if winner is not None:
        node["board_value"] = winner
        return node

    if depth == max_depth:
        node["board_value"] = "draw"
        return node

    moveset = set()
    next_player = "O" if player == "X" else "X"
    counter_move = None # TODO: REMOVE

    for move in legal_moves(board, gravity):
        next_board = apply_move(board, move, player, gravity)

        # ignore symmetries
        symmetries = board_symmetries(next_board, gravity)
        if len(moveset & symmetries) > 0: continue
        moveset |= symmetries

        # get next game state
        child_node = build_board_tree(next_board, next_player, rule, gravity, depth+1, max_depth)

        # play move if winning
        if child_node["board_value"] == player:
            node["board_value"] = child_node["board_value"]
            node["children"] = [child_node]
            return node

        # TODO: REMOVE
        # store counter move if stops opponent from winning
        if check_winner(apply_move(board, move, next_player, gravity)) == next_player:
            counter_move = child_node
        else:
            node["children"].append(child_node)

        # TODO: ADD
        """
        # append game state
        node["children"].append(child_node)
        """

    # TODO: REMOVE
    if counter_move:
        node["board_value"] = counter_move["board_value"]
        node["children"] = [counter_move]
        return node
    child_values = [child_node["board_value"] for child_node in node["children"]]
    if "draw" in child_values:
        node["board_value"] = "draw"
        node["children"] = [node["children"][child_values.index("draw")]]

    # TODO: ADD
    """
    child_values = [child_node["board_value"] for child_node in node["children"]]
    if "draw" in child_values:
        node["board_value"] = "draw"
        node["children"] = [node["children"][child_values.index("draw")]]
        return node
    node["board_value"] = next_player
    node["children"] = [node["children"][child_values.index(next_player)]]
    """

    return node

if __name__ == "__main__":

  # game rule constants (tic-tac-toe)
  ROWS, COLS = 3, 3
  N_SEQUENCE = 3
  GRAVITY = False

  # game rule constants (connect-4)
  # ROWS, COLS = 6, 7
  # N_SEQUENCE = 4
  # GRAVITY = True

  INITIAL_BOARD_STATE = new_board(rows=ROWS, cols=COLS)

  # first tic-tac-toe move placed in center
  FIRST_MOVE = apply_move(INITIAL_BOARD_STATE, (1, 1), player="X", gravity=GRAVITY)

  # first connect-4 move placed in middle column
  # FIRST_MOVE = apply_move(INITIAL_BOARD_STATE, 3, player="X", gravity=GRAVITY)

  board_tree = build_board_tree(FIRST_MOVE, player="O", rule=N_SEQUENCE, gravity=GRAVITY, depth=1, max_depth=42)
  draw_moves(board_tree, rows=ROWS, cols=COLS)
