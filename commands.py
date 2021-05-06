from typing import Dict
from abc import ABC


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


class CommandException(Exception):
    pass


class Command(ABC):
    """
    Incapsulates game protocol commands
    """
    def __init__(self, **parameters):
        pass


class WaitingCommand(Command):
    def __init__(self, **parameters):
        super().__init__()


class ErrorCommand(Command):
    def __init__(self, **parameters):
        super().__init__()
        self.message = parameters["msg"]


class StartedCommand(Command):
    def __init__(self, **parameters):
        super().__init__()
        self.opponent = parameters["opp_id"]
        self.ptype = parameters["ptype"]


class UpdateStateCommand(Command):
    def __init__(self, **parameters):
        super().__init__()
        self.board = parameters["board"]
        self.p_t_m = parameters["player_to_move"]
        self.last_move = parameters["last_move"]


class OfferedCommand(Command):
    def __init__(self, **parameters):
        super().__init__()


class GameOverCommand(Command):
    def __init__(self, **parameters):
        super().__init__()
        self.result = parameters["result"]
        self.win_pos = parameters["win_pos"]
        self.cause = parameters["cause"]


class ReadyCommand(Command):
    def __init__(self, **parameters):
        super().__init__()
        self.type = parameters["type"]
        self.opponent = parameters["oppponent"]


class ResignCommand(Command):
    def __init__(self, **parameters):
        super().__init__()


class MoveCommand(Command):
    def __init__(self, **parameters):
        super().__init__()
        self.square = parameters["square"]
        self.vertical = parameters["vertical"]
        self.horizontal = parameters["horizontal"]


class OfferCommand(Command):
    def __init__(self, **parameters):
        super().__init__()


class AcceptCommand(Command):
    def __init__(self, **parameters):
        super().__init__()


class CommandFactory(ABC):
    _commands = {
            "waiting": WaitingCommand,
            "error": ErrorCommand,
            "started": StartedCommand,
            "update_state": UpdateStateCommand,
            "offered": OfferCommand,
            "game_over": GameOverCommand,
            "ready": ReadyCommand,
            "resign": ResignCommand,
            "move": MoveCommand,
            "offer": OfferCommand,
            "accept": AcceptCommand,
    }

    @staticmethod
    def from_data(data: Dict) -> 'Command':
        if data["version"] == "v1":
            command_type = data["command"]
            parameters = data["parameters"]
        else:
            raise CommandException(f"Wrong protocol version {data['version']}!")
        if command_type not in _commands:
            raise CommandException(f"Unknown command {command_type} found!")
        return _commands[command_type](parameters)
