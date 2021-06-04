from global_defs import global_playground
from players import Entry, Game, Move
from db import add_game_to_db
from typing import Optional, Dict


async def add_new_entry(uid, data):
    player = global_playground.player(uid)
    entry = Entry(player)
    global_playground.add_entry(entry)


async def try_create_new_game(uid):
    game = None
    entry = global_playground.get_entry(uid)
    # check for suitable opponent
    match = global_playground.find_match(entry)
    if match is not None:
        # create new game
        game = global_playground.add_game(match)
    return game


async def resign_game(uid):
    game = None
    player = global_playground.player(uid)
    if player.is_playing():
        game = player.game
        result = "first_win" if player.side == "second" else "second_win"
        game.set_result(result)
        await add_game_to_db(game)
    return game


async def clear_game(game: Game):
    game.clear()


async def new_move(uid: str, data: Dict) -> Optional[Game]:
    game = None
    player = global_playground.player(uid)
    if player.is_playing():
        game = player.game
        game.set_new_move(Move.create_move(player.side, data['parameters']['square'],
                                           data['parameters']['vertical'], data['parameters']['horizontal']))
        game.update_result()
        if game.is_finished():
            # save game to db
            await add_game_to_db(game)
    return game
