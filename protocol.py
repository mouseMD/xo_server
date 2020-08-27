from players import active_players, ActivePlayer, \
    get_suitable_opponent, add_to_waiting_list, offers
import xo_app_stub
from db import add_game_to_db
import json


async def ready_handler(params, user_id, ws):
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
        xo_app_stub.release_game()
        await opp.ws.close()
    await ws.close()


async def move_handler(params, user_id, ws):
    player = active_players[user_id]
    opponent = active_players[player.opponent_id]
    # update game
    xo_app_stub.set_new_move()
    board = xo_app_stub.get_board()
    player_to_move = xo_app_stub.get_player_to_move()
    last_move = params
    responce1 = await construct_update_state(board, player_to_move, last_move)
    responce2 = await construct_update_state(board, player_to_move, last_move)
    await ws.send_json(responce1)
    await opponent.ws.send_json(responce2)
    # check for game over
    if xo_app_stub.finished():
        result = xo_app_stub.result()
        win_pos = xo_app_stub.get_win_coords()
        responce1 = await construct_game_over(result, win_pos, "win rule")
        responce2 = await construct_game_over(result, win_pos, "win rule")
        await ws.send_json(responce1)
        await opponent.ws.send_json(responce2)
        # save game to db
        moves = xo_app_stub.get_moves()
        await add_game_to_db()
        # remove game from app
        xo_app_stub.release_game()
        await opponent.ws.close()
        await ws.close()


async def offer_handler(params, user_id, ws):
    player = active_players[user_id]
    opponent = active_players[player.opponent_id]

    # if answer to offer
    if opponent in offers:
        offers.remove(opponent)
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
        xo_app_stub.release_game()
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
            print('unknown command {} found!'.format(command))
    else:
        print('Not supported protocol version: {} found!'.format(cmd_data['version']))


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


async def construct_started(opp_id, ptype):
    data = {
        "version": "v1",
        "command": "started",
        "parameters": {
            "opponent": opp_id,
            "ptype": ptype
        }
    }
    return json.dumps(data)


async def construct_update_state(board, p_t_m, last_move):
    data = {
        "version": "v1",
        "command": "started",
        "parameters": {
            "board": board,
            "player_to_move": p_t_m,
            "last_move": last_move
        }
    }
    return json.dumps(data)


async def construct_offered():
    data = {
        "version": "v1",
        "command": "offered",
        "parameters": {
        }
    }
    return json.dumps(data)


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
    return json.dumps(data)
