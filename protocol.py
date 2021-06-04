from db import add_game_to_db
import logging
from global_defs import global_playground, registry
from players import Move, NotRegistered, NotIdleException, WrongPlayerException
from commands import *
from typing import Dict, List, Optional
from logic import add_new_entry, try_create_new_game, resign_game, clear_game


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
            await send_command(GameOverCommand(opp_id, result=result, win_pos=None, cause="interruption"))

            game.set_result(result)
            await add_game_to_db(game)
            game.clear()
            global_playground.unregister(user_id)
    finally:
        registry.remove_socket(user_id)


async def handle_command(cmd_data: Dict, user_id):
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
    user_id = cmd.user_id
    try:
        await add_new_entry(user_id, cmd.data())
    except NotIdleException:
        res_commands.append(ErrorCommand(user_id, msg="New entry rejected, already waiting game or playing"))
    else:
        res_commands.append(WaitingCommand(user_id))
        game = await try_create_new_game(user_id)
        if game is not None:
            # send "started" responses to both players
            first_id = game.first().player_id
            second_id = game.second().player_id
            res_commands.append(StartedCommand(first_id, opp_id=second_id, ptype="first"))
            res_commands.append(StartedCommand(second_id, opp_id=first_id, ptype="second"))

            # send "update_state" responses to both players
            res_commands.append(UpdateStateCommand.from_game(first_id, game))
            res_commands.append(UpdateStateCommand.from_game(second_id, game))
    return res_commands


async def execute_resign_handler(cmd: ResignCommand) -> List[Optional[Command]]:
    logging.info(f"Handling 'resign' command: {str(cmd)}")
    res_commands = []
    user_id = cmd.user_id
    game = await resign_game(user_id)
    if game is not None:
        first_id = game.first().player_id
        second_id = game.second().player_id
        res_commands.append(GameOverCommand.from_game(first_id, game, "resignation"))
        res_commands.append(GameOverCommand.from_game(second_id, game, "resignation"))
        await clear_game(game)
    else:
        res_commands.append(ErrorCommand(user_id, msg='Resign rejected, no current game'))
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
    await ws.send_json(cmd.data())
