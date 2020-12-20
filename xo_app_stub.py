import xo_app
from typing import Sequence

ga = xo_app.GameApplication()


class InvalidCoordsException(Exception):
    def __init__(self):
        super().__init__()


class InvalidPlayerException(Exception):
    def __init__(self):
        super().__init__()


def create_new_game() -> int:
    """
    Allocate memory for a new game.

    Returns unique game id.
    """
    return ga.create_new_game()


def set_new_move(game_index: int, player: str, coords: Sequence) -> None:
    """
    Make a new move in game.

    coords must be sequence of 3 valid numbers.
    player must be one of options: 'first' or 'second'.
    """
    if len(coords) != 3:
        raise InvalidCoordsException()
    try:
        for item in coords:
            if item < 0 or item > 3:
                raise InvalidCoordsException()
    except TypeError:
        raise InvalidCoordsException()
    c = xo_app.Coordinates(*coords)

    if player == 'first':
        p = xo_app.Player.X_Player
    elif player == 'second':
        p = xo_app.Player.O_Player
    else:
        raise InvalidPlayerException()
    ga.set_new_move(game_index, p, c)


def release_game(game_index) -> None:
    """
    Delete game data.
    """
    ga.release_game(game_index)


def finalize() -> None:
    """
    Free all resources used by application.
    """
    ga.finalize()


def finished(game_index) -> bool:
    """
    Check if the game is in its final state.
    """
    return ga.finished(game_index)


def result(game_index) -> str:
    """
    Return result of the game.
    """
    results = {0: 'first_win',
               1: 'second_win',
               2: 'draw',
               3: 'none'}
    int_result = ga.result(game_index)
    return results[int_result]


def get_moves(game_index) -> str:
    """
    Return all moves from the game.
    """
    return ga.get_moves(game_index)


def get_win_coords(game_index) -> str:
    """
    Return squares of win combination.
    """
    return ga.get_win_coords(game_index)


def get_board(game_index) -> str:
    """
    Return full board shapshot.
    """
    return ga.get_board(game_index)


def get_player_to_move(game_index) -> str:
    """
    Return player to move now.

    Return values are 'first' or 'second'.
    """
    p = ga.get_player_to_move(game_index)
    return 'first' if p == xo_app.Player.X_Player else 'second'
