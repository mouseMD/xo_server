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
    ga.finalize()


def finished(game_index):
    return ga.finished(game_index)


def started(game_index):
    return ga.started(game_index)


def result(game_index):
    return ga.result(game_index)


def get_moves(game_index):
    return ga.get_moves(game_index)


def get_win_coords(game_index):
    return ga.get_win_coords(game_index)


def exist(game_index):
    return ga.exist(game_index)


def get_board(game_index):
    return ga.get_board(game_index)


def get_player_to_move(game_index):
    p = ga.get_player_to_move(game_index)
    return 'first' if p == xo_app.Player.X_Player else 'second'
