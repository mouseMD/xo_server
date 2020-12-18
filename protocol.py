from players import active_players, ActivePlayer, \
    get_suitable_opponent, add_to_waiting_list, offers
import xo_app_stub
from db import add_game_to_db
import logging
from global_defs import global_sockets, global_playground


async def ready_handler(params, user_id, ws):
    logging.info("Handling 'ready' command, user_id : {}".format(user_id))
    # add new active player
    player = ActivePlayer(ws)
    active_players[user_id] = player
    # check if exist suitable opponent
    match_data = await get_suitable_opponent(params)
    if match_data is not None:
        # create new game in app
        opp_id = match_data[0]
        ptype = 'first' if match_data[1] == 0 else 'second'
        opp_ptype = 'second' if match_data[1] == 0 else 'first'
        game_id = xo_app_stub.create_new_game()
        opponent = active_players[opp_id]
        opponent.start_game(game_id, user_id, opp_ptype)
        player.start_game(game_id, opp_id, ptype)
        # send "started" responces to both players
        responce1 = await construct_started(opp_id, opp_ptype)
        responce2 = await construct_started(user_id, ptype)
        await ws.send_json(responce1)
        await opponent.ws.send_json(responce2)
    else:
        await add_to_waiting_list(user_id, {})


async def resign_handler(params, user_id, ws):
    logging.info("Handling 'resign' command, user_id : {}".format(user_id))
    # remove active player and stop game if exists
    player = active_players.pop(user_id)
    if player.game_id is not None:
        opp = active_players.pop(player.opponent_id)
        responce1 = await construct_game_over(result="loss",
                                              win_pos=None,
                                              cause="resignation")
        responce2 = await construct_game_over(result="win",
                                              win_pos=None,
                                              cause="resignation")
        await ws.send_json(responce1)
        await opp.ws.send_json(responce2)
        # save game to db
        await add_game_to_db()
        # remove game from app
        xo_app_stub.release_game(player.game_id)
        await opp.ws.close()
    await ws.close()


async def move_handler(params, user_id, ws):
    logging.info("Handling 'move' command, user_id : {}".format(user_id))
    player = active_players[user_id]
    opponent = active_players[player.opponent_id]
    # update game
    game_id = player.game_id
    xo_app_stub.set_new_move(game_id, player.ptype,
                             [params['square'], params['vertical'], params['horizontal']])
    board = xo_app_stub.get_board(game_id)
    player_to_move = xo_app_stub.get_player_to_move(game_id)
    last_move = params
    responce1 = await construct_update_state(board, player_to_move, last_move)
    responce2 = await construct_update_state(board, player_to_move, last_move)
    await ws.send_json(responce1)
    await opponent.ws.send_json(responce2)
    # check for game over
    if xo_app_stub.finished(game_id):
        result = xo_app_stub.result(game_id)
        win_pos = xo_app_stub.get_win_coords(game_id)
        responce1 = await construct_game_over(result, win_pos, "win rule")
        responce2 = await construct_game_over(result, win_pos, "win rule")
        await ws.send_json(responce1)
        await opponent.ws.send_json(responce2)
        # save game to db
        moves = xo_app_stub.get_moves(game_id)
        await add_game_to_db()
        # remove game from app
        xo_app_stub.release_game(game_id)
        await opponent.ws.close()
        await ws.close()


async def offer_handler(params, user_id, ws):
    logging.info("Handling 'offer' command, user_id : {}".format(user_id))
    player = active_players[user_id]
    opponent = active_players[player.opponent_id]

    # if answer to offer
    if player.opponent_id in offers:
        offers.remove(player.opponent_id)
        responce1 = await construct_game_over(result="draw",
                                              win_pos=None,
                                              cause="agreement")
        responce2 = await construct_game_over(result="draw",
                                              win_pos=None,
                                              cause="agreement")
        await ws.send_json(responce1)
        await opponent.ws.send_json(responce2)
        # save game to db
        await add_game_to_db()
        # remove game from app
        xo_app_stub.release_game(player.game_id)
        await opponent.ws.close()
        await ws.close()
    else:
        offers.append(user_id)
        responce = await construct_offered()
        await opponent.ws.send_json(responce)


async def handle_command(cmd_data, user_id, ws):
    if cmd_data["version"] == "v1":
        command = cmd_data["command"]
        parameters = cmd_data["parameters"]

        command_handlers = {
            'ready': ready_handler,
            'resign': resign_handler,
            'move': move_handler,
            'offer': offer_handler
        }

        if command in command_handlers:
            await command_handlers[command](parameters, user_id, ws)
        else:
            logging.info('unknown command {} found! user_id: {}'.format(command, user_id))
    else:
        logging.info('Not supported protocol version: {} found! user_id: {}'.format(cmd_data['version'], user_id))


async def handle_error(user_id):
    # remove active player and stop game if exists
    player = active_players.pop(user_id)
    if player.game_id is not None:
        opp = active_players.pop(player.opponent_id)
        responce = await construct_game_over(result="win",
                                             win_pos=None,
                                             cause="interruption")
        await opp.ws.send_json(responce)
        # save game to db
        await add_game_to_db()
        # remove game from app
        xo_app_stub.release_game()
        await opp.ws.close()


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
