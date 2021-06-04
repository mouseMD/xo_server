from global_defs import global_playground
from players import Entry


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
