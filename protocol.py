from db import add_game_to_db
import logging
from global_defs import global_playground, registry
from players import Entry, AlreadyPlaying, Move, NotRegistered, AlreadyWaiting, NotIdleException, WrongPlayerException
from commands import *
from typing import Dict, List, Optional


async def ready_handler(params, user_id, ws):
    logging.info("Handling 'ready' command, user_id : {}".format(user_id))
    try:
        player = global_playground.player(user_id)
        entry = Entry(player, params)
        global_playground.add_entry(entry)
    except NotIdleException:
        await ws.send_json(await construct_error('New entry rejected, already waiting game or playing'))
    else:
        await ws.send_json(await construct_waiting())
        # check for suitable opponent
        match = global_playground.find_match(entry)
        if match is not None:
            # create new game
            game = global_playground.add_game(match)
            # send "started" responces to both players
            opp_id = player.opp.player_id
            response1 = await construct_started(opp_id, player.side)
            response2 = await construct_started(user_id, player.opp.side)
            await ws.send_json(response1)
            await registry.get_socket(opp_id).send_json(response2)
            # send "update_state" responces to both players
            board = game.get_board()
            player_to_move = game.player_to_move()
            last_move = None
            response3 = await construct_update_state(board, player_to_move, last_move)
            response4 = await construct_update_state(board, player_to_move, last_move)
            await ws.send_json(response3)
            await registry.get_socket(opp_id).send_json(response4)


async def resign_handler(params, user_id, ws):
    logging.info("Handling 'resign' command, user_id : {}".format(user_id))
    player = global_playground.player(user_id)
    if player.is_playing():
        game = player.game
        result = "first_win" if player.side == "second" else "second_win"
        game.set_result(result)
        await add_game_to_db(game)
        opp_id = player.opp.player_id
        game.clear()
        response1 = await construct_game_over(result=result,
                                              win_pos=None,
                                              cause="resignation")
        response2 = await construct_game_over(result=result,
                                              win_pos=None,
                                              cause="resignation")
        await ws.send_json(response1)
        await registry.get_socket(opp_id).send_json(response2)
    else:
        await ws.send_json(await construct_error('Resign rejected, no current game'))


async def move_handler(params, user_id, ws):
    logging.info("Handling 'move' command, user_id : {}".format(user_id))
    player = global_playground.player(user_id)
    if player.is_playing():
        game = player.game
        try:
            game.set_new_move(Move.create_move(player.side,
                                           params['square'], params['vertical'], params['horizontal']))
        except WrongPlayerException:
            await ws.send_json(await construct_error('Move rejected, not your move'))
        else:
            game.update_result()
            board = game.get_board()
            player_to_move = game.player_to_move()
            last_move = params
            response1 = await construct_update_state(board, player_to_move, last_move)
            response2 = await construct_update_state(board, player_to_move, last_move)
            await ws.send_json(response1)
            opp_id = player.opp.player_id
            await registry.get_socket(opp_id).send_json(response2)
            # check for game over by rules of board
            if game.is_finished():
                result = game.get_result()
                win_pos = game.get_win_pos()
                response1 = await construct_game_over(result, win_pos, "win rule")
                response2 = await construct_game_over(result, win_pos, "win rule")
                await ws.send_json(response1)
                await registry.get_socket(opp_id).send_json(response2)
                # save game to db
                await add_game_to_db(game)
                game.clear()
    else:
        await ws.send_json(await construct_error('New move rejected, no current game'))


async def offer_handler(params, user_id, ws):
    logging.info("Handling 'offer' command, user_id : {}".format(user_id))
    player = global_playground.player(user_id)
    if player.is_playing():
        game = player.game
        game.set_draw_offer(player.opp)
        responce = await construct_offered()
        opp_id = player.opp.player_id
        await registry.get_socket(opp_id).send_json(responce)
    else:
        await ws.send_json(await construct_error('Draw offer rejected, no current game'))


async def accept_hadler(params, user_id, ws):
    logging.info("Handling 'accept' command, user_id : {}".format(user_id))
    player = global_playground.player(user_id)
    if player.is_playing():
        game = player.game
        if game.can_accept is player:
            # fix the draw
            game.set_result('draw')
            response1 = await construct_game_over('draw', None, "agreement")
            response2 = await construct_game_over('draw', None, "agreement")
            await ws.send_json(response1)
            opp_id = player.opp.player_id
            await registry.get_socket(opp_id).send_json(response2)
            # save game to db
            await add_game_to_db(game)
            game.clear()
        else:
            await ws.send_json(await construct_error('Cannot accept, no offer'))
    else:
        await ws.send_json(await construct_error('Draw accept rejected, no current game'))


async def handle_command(cmd_data, user_id, ws):
    if cmd_data["version"] == "v1":
        command = cmd_data["command"]
        parameters = cmd_data["parameters"]

        command_handlers = {
            'ready': ready_handler,
            'resign': resign_handler,
            'move': move_handler,
            'offer': offer_handler,
            'accept': accept_hadler
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
    except NotIdleException:
        player = global_playground.player(user_id)
        if player.is_waiting():
            # there is entry, there is no game
            global_playground.remove_entry(user_id)
            global_playground.unregister(user_id)
        elif player.is_playing():
            # there is game, there is no entry
            opp_id = player.opp.player_id
            game = player.game
            result = "first_win" if player.side == "second" else "second_win"
            response = await construct_game_over(result=result,
                                                 win_pos=None,
                                                 cause="interruption")
            await registry.get_socket(opp_id).send_json(response)
            game.set_result(result)
            await add_game_to_db(game)
            game.clear()
            global_playground.unregister(user_id)
    finally:
        registry.remove_socket(user_id)


async def handle_command_new(cmd_data: Dict, user_id, ws):
    """
    """
    try:
        result_commands = await execute_logic(CommandFactory.from_data(user_id, cmd_data))
    except CommandException as exp:
        logging.info(exp.args)
    else:
        for command in result_commands:
            await send_command(command)


async def execute_logic(cmd: Command) -> List[Optional[Command]]:
    """
    Business logic of game commands.
    """
    command_handlers = {
        ReadyCommand: execute_ready_handler,
        ResignCommand: execute_resign_handler,
        MoveCommand: execute_move_handler,
        OfferCommand: execute_offer_handler,
        AcceptCommand: execute_accept_handler
    }
    command_type = type(cmd)
    if command_type in command_handlers:
        result = await command_handlers[command_type](cmd)
    else:
        result = []
    return result


async def execute_ready_handler(cmd: ReadyCommand) -> List[Optional[Command]]:
    logging.info(f"Handling 'ready' command: {str(cmd)}")
    res_commands = []
    try:
        player = global_playground.player(cmd.user_id)
        entry = Entry(player)
        global_playground.add_entry(entry)
    except NotIdleException:
        res_commands.append(ErrorCommand(cmd.user_id, msg="New entry rejected, already waiting game or playing"))
    else:
        res_commands.append(WaitingCommand(cmd.user_id))
        # check for suitable opponent
        match = global_playground.find_match(entry)
        if match is not None:
            # create new game
            game = global_playground.add_game(match)
            # send "started" responces to both players
            opp_id = player.opp.player_id
            res_commands.append(StartedCommand(cmd.user_id, opp_id=opp_id, ptype=player.side))
            res_commands.append(StartedCommand(opp_id, opp_id=cmd.user_id, ptype=player.opp.side))

            # send "update_state" responces to both players
            board = game.get_board()
            player_to_move = game.player_to_move()
            last_move = None
            res_commands.append(UpdateStateCommand(cmd.user_id, board=board, player_to_move=player_to_move,
                                                   last_move=last_move))
            res_commands.append(UpdateStateCommand(opp_id, board=board, player_to_move=player_to_move,
                                                   last_move=last_move))
    return res_commands


async def execute_resign_handler(cmd: ResignCommand) -> List[Optional[Command]]:
    logging.info(f"Handling 'resign' command: {str(cmd)}")
    res_commands = []
    player = global_playground.player(cmd.user_id)
    if player.is_playing():
        game = player.game
        result = "first_win" if player.side == "second" else "second_win"
        game.set_result(result)
        await add_game_to_db(game)
        opp_id = player.opp.player_id
        game.clear()
        res_commands.append(GameOverCommand(cmd.user_id, result=result, win_pos=None, cause="resignation"))
        res_commands.append(GameOverCommand(opp_id, result=result, win_pos=None, cause="resignation"))
    else:
        res_commands.append(ErrorCommand(cmd.user_id, msg='Resign rejected, no current game'))
    return res_commands


async def execute_move_handler(cmd: MoveCommand) -> List[Optional[Command]]:
    logging.info(f"Handling 'move' command, user_id : {str(cmd)}")
    res_commands = []
    player = global_playground.player(cmd.user_id)
    if player.is_playing():
        game = player.game
        try:
            game.set_new_move(Move.create_move(player.side, cmd.square, cmd.vertical, cmd.horizontal))
        except WrongPlayerException:
            res_commands.append(ErrorCommand(cmd.user_id, msg='Move rejected, not your move'))
        else:
            game.update_result()
            board = game.get_board()
            player_to_move = game.player_to_move()
            last_move = None
            opp_id = player.opp.player_id
            res_commands.append(UpdateStateCommand(cmd.user_id, board=board, player_to_move=player_to_move,
                                                   last_move=last_move))
            res_commands.append(UpdateStateCommand(opp_id, board=board, player_to_move=player_to_move,
                                                   last_move=last_move))
            # check for game over by rules of board
            if game.is_finished():
                result = game.get_result()
                win_pos = game.get_win_pos()
                res_commands.append(GameOverCommand(cmd.user_id, result=result, win_pos=win_pos, cause="win rule"))
                res_commands.append(GameOverCommand(opp_id, result=result, win_pos=win_pos, cause="win rule"))

                # save game to db
                await add_game_to_db(game)
                game.clear()
    else:
        res_commands.append(ErrorCommand(cmd.user_id, msg='New move rejected, no current game'))
    return res_commands


async def execute_offer_handler(cmd: OfferCommand) -> List[Optional[Command]]:
    logging.info(f"Handling 'offer' command: {str(cmd)}")
    res_commands = []
    player = global_playground.player(cmd.user_id)
    if player.is_playing():
        game = player.game
        game.set_draw_offer(player.opp)
        opp_id = player.opp.player_id
        res_commands.append(OfferedCommand(opp_id))
    else:
        res_commands.append(ErrorCommand(cmd.user_id, msg='Draw offer rejected, no current game'))
    return res_commands


async def execute_accept_handler(cmd: AcceptCommand) -> List[Optional[Command]]:
    logging.info(f"Handling 'accept' command, user_id : {str(cmd)}")
    res_commands = []
    player = global_playground.player(cmd.user_id)
    if player.is_playing():
        game = player.game
        if game.can_accept is player:
            # fix the draw
            game.set_result('draw')
            opp_id = player.opp.player_id
            res_commands.append(GameOverCommand(cmd.user_id, result='draw', win_pos=None, cause='agreement'))
            res_commands.append(GameOverCommand(opp_id, result='draw', win_pos=None, cause='agreement'))

            # save game to db
            await add_game_to_db(game)
            game.clear()
        else:
            res_commands.append(ErrorCommand(cmd.user_id, msg='Cannot accept, no offer'))
    else:
        res_commands.append(ErrorCommand(cmd.user_id, msg='Draw accept rejected, no current game'))
    return res_commands


async def send_command(cmd: Command) -> None:
    """
    """
    ws = registry.get_socket(cmd.user_id)
    ws.send_json(cmd.data())
