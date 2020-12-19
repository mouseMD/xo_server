from players import active_players, ActivePlayer, \
    get_suitable_opponent, add_to_waiting_list, offers
import xo_app_stub
from db import add_game_to_db
import logging
from global_defs import global_sockets, global_playground
from players import Entry, AlreadyPlaying, Move, NotRegistered, AlreadyWaiting


async def ready_handler(params, user_id, ws):
    logging.info("Handling 'ready' command, user_id : {}".format(user_id))
    try:
        global_playground.add_entry(Entry.from_params(user_id, params))
    except AlreadyPlaying:
        await ws.send_json(await construct_error('New entry rejected, already waiting game or playing'))
    else:
        await ws.send_json(await construct_waiting())
        # check for suitable opponent
        opp_id = global_playground.find_match(user_id)
        if opp_id is not None:
            # create new game
            global_playground.add_game(user_id, opp_id)
            # send "started" responces to both players
            response1 = await construct_started(opp_id, global_playground.side(opp_id))
            response2 = await construct_started(user_id, global_playground.side(user_id))
            await ws.send_json(response1)
            await global_sockets[opp_id].send_json(response2)


async def resign_handler(params, user_id, ws):
    logging.info("Handling 'resign' command, user_id : {}".format(user_id))
    # remove active player and stop game if exists
    # save game to db
    await add_game_to_db()
    opp_id = global_playground.opp_id(user_id)
    global_playground.remove_game(global_playground.game_id(user_id))
    response1 = await construct_game_over(result="loss",
                                          win_pos=None,
                                          cause="resignation")
    response2 = await construct_game_over(result="win",
                                          win_pos=None,
                                          cause="resignation")
    await ws.send_json(response1)
    await global_sockets[opp_id].send_json(response2)


async def move_handler(params, user_id, ws):
    logging.info("Handling 'move' command, user_id : {}".format(user_id))
    game_id = global_playground.game_id(user_id)
    game = global_playground.game(game_id)
    game.set_new_move(Move.create_move(global_playground.side(user_id),
                                       params['square'], params['vertical'], params['horizontal']))
    board = game.get_board()
    player_to_move = game.player_to_move()
    last_move = params
    response1 = await construct_update_state(board, player_to_move, last_move)
    response2 = await construct_update_state(board, player_to_move, last_move)
    await ws.send_json(response1)
    opp_id = global_playground.opp_id(user_id)
    await global_sockets[opp_id].send_json(response2)
    # check for game over by rules of board
    if game.is_finished():
        result = game.get_result()
        win_pos = game.get_win_pos()
        response1 = await construct_game_over(result, win_pos, "win rule")
        response2 = await construct_game_over(result, win_pos, "win rule")
        await ws.send_json(response1)
        await global_sockets[opp_id].send_json(response2)
        # save game to db
        moves = game.get_moves()
        await add_game_to_db()
        global_playground.remove_game(game_id)


async def handle_command(cmd_data, user_id, ws):
    if cmd_data["version"] == "v1":
        command = cmd_data["command"]
        parameters = cmd_data["parameters"]

        command_handlers = {
            'ready': ready_handler,
            'resign': resign_handler,
            'move': move_handler,
            #'offer': offer_handler
        }

        if command in command_handlers:
            await command_handlers[command](parameters, user_id, ws)
        else:
            logging.info('unknown command {} found! user_id: {}'.format(command, user_id))
    else:
        logging.info('Not supported protocol version: {} found! user_id: {}'.format(cmd_data['version'], user_id))


async def handle_error(user_id):
    # player with user_id disconnected or error happened
    try:
        global_playground.unregister(user_id)
    except NotRegistered:
        pass
    except AlreadyWaiting:
        # there is entry, there is no game
        global_playground.remove_entry(user_id)
        global_playground.unregister(user_id)
    except AlreadyPlaying:
        # there is game, there is no entry
        opp_id = global_playground.opp_id(user_id)
        response = await construct_game_over(result="win",
                                             win_pos=None,
                                             cause="interruption")
        await global_sockets[opp_id].send_json(response)
        # save game to db
        game_id = global_playground.game_id(user_id)
        game = global_playground.game(game_id)
        moves = game.get_moves()
        await add_game_to_db()
        global_playground.remove_game(game_id)
        global_playground.unregister(user_id)
    finally:
        global_sockets.pop(user_id)


async def construct_waiting():
    data = {
        'version': 'v1',
        'command': 'waiting',
        'parameters': {}
    }
    return data


async def construct_error(msg):
    data = {
        'version': 'v1',
        'command': 'error',
        'parameters': {
            'message': msg
        }
    }
    return data


async def construct_started(opp_id, ptype):
    data = {
        'version': 'v1',
        "command": "started",
        "parameters": {
            "opponent": opp_id,
            "ptype": ptype
        }
    }
    return data


async def construct_update_state(board, p_t_m, last_move):
    data = {
        "version": "v1",
        "command": "update_state",
        "parameters": {
            "board": board,
            "player_to_move": p_t_m,
            "last_move": last_move
        }
    }
    return data


async def construct_offered():
    data = {
        "version": "v1",
        "command": "offered",
        "parameters": {
        }
    }
    return data


async def construct_game_over(result, win_pos, cause):
    data = {
        "version": "v1",
        "command": "game_over",
        "parameters": {
            "result": result,
            "win_pos": win_pos,
            "cause": cause
        }
    }
    return data
