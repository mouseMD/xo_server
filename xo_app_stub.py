import xo_app

ga = xo_app.GameApplication()


def create_new_game():
    return ga.create_new_game()


def set_new_move(game_index, player, coords):
    c = xo_app.Coordinates(*coords)
    p = xo_app.Player.X_Player if player == 'first' else xo_app.Player.O_Player
    ga.set_new_move(game_index, p, c)


def release_game(game_index):
    ga.release_game(game_index)


def finalize():
    pass


def finished(game_index):
    return ga.finished(game_index)


def started():
    pass


def result(game_index):
    return ga.result(game_index)


def get_moves(game_index):
    return ga.get_moves(game_index)


def get_win_coords(game_index):
    return ga.get_win_coords(game_index)


def exist():
    pass


def get_board(game_index):
    return [0]*64


def get_player_to_move(game_index):
    return 1
