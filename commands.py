from typing import Dict
from abc import ABC, abstractmethod
from players import Game


class CommandException(Exception):
    pass


class Command(ABC):
    """
    Incapsulates game protocol commands
    """
    def __init__(self, user_id):
        self.user_id = user_id

    @abstractmethod
    def data(self):
        pass

    def __str__(self):
        return str(self.__dict__)


class InCommand(Command):
    """
    Input commands (from user to server)
    """
    def __init__(self, user_id):
        super().__init__(user_id)
        self.direction = "in"

    @abstractmethod
    def data(self):
        pass


class OutCommand(Command):
    """
    Output commands (from server to user)
    """
    def __init__(self, user_id):
        super().__init__(user_id)
        self.direction = "out"

    @abstractmethod
    def data(self):
        pass


class WaitingCommand(OutCommand):
    def __init__(self, user_id, **parameters):
        super().__init__(user_id)

    def data(self):
        return {
            'version': 'v1',
            'command': 'waiting',
            'parameters': {}
        }


class ErrorCommand(OutCommand):
    def __init__(self, user_id, **parameters):
        super().__init__(user_id)
        self.message = parameters["msg"]

    def data(self):
        params = {
            'msg': self.message
        }
        return {
            'version': 'v1',
            'command': 'error',
            'parameters': params
        }


class StartedCommand(OutCommand):
    def __init__(self, user_id, **parameters):
        super().__init__(user_id)
        self.opponent = parameters["opp_id"]
        self.ptype = parameters["ptype"]

    def data(self):
        params = {
            'opp_id': self.opponent,
            'ptype': self.ptype
        }
        return {
            'version': 'v1',
            'command': 'started',
            'parameters': params
        }


class UpdateStateCommand(OutCommand):
    def __init__(self, user_id, **parameters):
        super().__init__(user_id)
        self.board = parameters["board"]
        self.p_t_m = parameters["player_to_move"]
        self.last_move = parameters["last_move"]

    def data(self):
        params = {
            'board': self.board,
            'player_to_move': self.p_t_m,
            'last_move': self.last_move
        }
        return {
            'version': 'v1',
            'command': 'update_state',
            'parameters': params
        }

    @staticmethod
    def from_game(user_id, game: Game) -> 'UpdateStateCommand':
        cmd = UpdateStateCommand(user_id, board=game.get_board(), player_to_move=game.player_to_move(),
                                 last_move=game.get_last_move())
        return cmd


class OfferedCommand(OutCommand):
    def __init__(self, user_id, **parameters):
        super().__init__(user_id)

    def data(self):
        return {
            'version': 'v1',
            'command': 'offered',
            'parameters': {}
        }


class GameOverCommand(OutCommand):
    def __init__(self, user_id, **parameters):
        super().__init__(user_id)
        self.result = parameters["result"]
        self.win_pos = parameters["win_pos"]
        self.cause = parameters["cause"]

    def data(self):
        params = {
            'result': self.result,
            'win_pos': self.win_pos,
            'cause': self.cause
        }
        return {
            'version': 'v1',
            'command': 'game_over',
            'parameters': params
        }


class ReadyCommand(InCommand):
    def __init__(self, user_id, **parameters):
        super().__init__(user_id)
        self.type = parameters["type"]
        self.opponent = parameters["opponent"]

    def data(self):
        params = {
            'type': self.type,
            'opponent': self.opponent,
        }
        return {
            'version': 'v1',
            'command': 'ready',
            'parameters': params
        }


class ResignCommand(InCommand):
    def __init__(self, user_id, **parameters):
        super().__init__(user_id)

    def data(self):
        return {
            'version': 'v1',
            'command': 'resign',
            'parameters': {}
        }


class MoveCommand(InCommand):
    def __init__(self, user_id, **parameters):
        super().__init__(user_id)
        self.square = parameters["square"]
        self.vertical = parameters["vertical"]
        self.horizontal = parameters["horizontal"]

    def data(self):
        params = {
            'square': self.square,
            'vertical': self.vertical,
            'horizontal': self.horizontal
        }
        return {
            'version': 'v1',
            'command': 'move',
            'parameters': params
        }


class OfferCommand(InCommand):
    def __init__(self, user_id, **parameters):
        super().__init__(user_id)

    def data(self):
        return {
            'version': 'v1',
            'command': 'offer',
            'parameters': {}
        }


class AcceptCommand(InCommand):
    def __init__(self, user_id, **parameters):
        super().__init__(user_id)

    def data(self):
        return {
            'version': 'v1',
            'command': 'accept',
            'parameters': {}
        }


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
    def from_data(user_id, data: Dict) -> 'Command':
        if data["version"] == "v1":
            command_type = data["command"]
            parameters = data["parameters"]
        else:
            raise CommandException(f"Wrong protocol version {data['version']}!")
        if command_type not in CommandFactory._commands:
            raise CommandException(f"Unknown command {command_type} found!")
        return CommandFactory._commands[command_type](user_id, **parameters)
