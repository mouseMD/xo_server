import xo_app_stub
from typing import Optional


class Entry:
    def __init__(self):
        self.user_id = None
        self.game_type = None
        self.side = None
        self.requested_user_id = None
        self.entry_type = None  # broadcast, bot, user

    @staticmethod
    def from_params(user_id, params):
        e = Entry()
        e.user_id = user_id
        return e

    def match(self, entry):
        return True


class Player:
    def __init__(self, player_id):
        self.player_id = player_id
        self.game_id = None
        self.side = None
        self.entry = None
        self.status = "idle"
        self.opp_id = None

    def add_entry(self, entry):
        self.entry = entry
        self.status = "waiting"

    def remove_entry(self):
        self.entry = None
        self.status = "idle"

    def add_game(self, game):
        self.game_id = game.game_id
        for key, val in game.players:
            if val == self.player_id:
                self.side = key
            else:
                self.opp_id = val

        self.entry = None
        self.status = "playing"

    def remove_game(self):
        self.game_id = None
        self.side = None
        self.status = "idle"
        self.opp_id = None


class ConnectedPlayer(Player):
    def __init__(self, player_id, ws):
        super().__init__(player_id)
        self.ws = ws


class Move:
    def __init__(self):
        self.square = None
        self.vertical = None
        self.horizontal = None
        self.player_to_move = None

    @staticmethod
    def create_move(sq, ver, hor, ptm):
        m = Move()
        m.square = sq
        m.vertical = ver
        m.horizontal = hor
        m.player_to_move = ptm
        return m


class GameException(Exception):
    def __init__(self):
        super().__init__()


class GameAlreadyRunningException(GameException):
    def __init__(self):
        super().__init__()


class GameNotReadyException(GameException):
    def __init__(self):
        super().__init__()


class GameNotRunningException(GameException):
    def __init__(self):
        super().__init__()


class WrongPlayerException(GameException):
    def __init__(self):
        super().__init__()


class WrongResultException(GameException):
    def __init__(self):
        super().__init__()


class Game:
    """
    Wraps game state and logic.
    """
    def __init__(self):
        self.game_id = None
        self.players = {}   # {"first" : uid1, "second" : uid2}
        self.status = "idle"
        self.game_type = None
        self.result = 'none'

    def setup(self, entry1: Entry, entry2: Entry) -> None:
        """
        Setup game state before starting actual play based on players' entries.

        If called when game is in 'running' state, raises GameAlreadyRunnningException().
        """
        if self.status == "waiting":
            self.game_type = entry1.game_type   # or entry2.game_type
            if entry1.side == "first" or entry2.side == "second":
                self.players = {"first": entry1.user_id, "second": entry2.user_id}
            else:
                self.players = {"first": entry2.user_id, "second": entry1.user_id}
            # todo here should be call for player.add_game(), but now there is no references to players
            self.status = "ready"
        else:
            raise GameAlreadyRunningException()

    def start(self) -> int:
        """
        Start actual game by calling game creation from xo_app.

        Returns integer - unique global game id.
        If called when game is not in 'ready' state, raises GameNotReadyException().
        """
        if self.status != 'ready':
            raise GameNotReadyException()
        self.game_id = xo_app_stub.create_new_game()
        self.status = "running"
        return self.game_id

    def clear(self) -> None:
        """
        Remove actual game.

        Game transits to 'idle' state.
        """
        if self.status == "running":
            xo_app_stub.release_game(self.game_id)
        self.game_id = None
        self.players = {}
        self.status = "idle"
        self.game_type = None

    def first(self) -> str:
        """
        Return user id for the first player.

        Game must be in 'ready' or 'running' state, else GameNotReadyException() is raised.
        """
        if self.status == 'idle':
            raise GameNotReadyException()
        return self.players["first"]

    def second(self) -> str:
        """
        Return user id for the second player.

        Game must be in 'ready' or 'running' state, else GameNotReadyException() is raised.
        """
        if self.status == 'idle':
            raise GameNotReadyException()
        return self.players["second"]

    def set_result(self, res: str) -> None:
        """
        Deliberately set result of game.

        Used for situation such as resignation, draw agreement or disconnection.
        Game must be in 'running' state, else GameNotRunningException() is raised.
        Accepted results: 'first_win', 'second_win', 'draw', 'none'.
        """
        if self.status != 'running':
            raise GameNotRunningException()
        results = {'first_win', 'second_win', 'draw', 'none'}
        if res not in results:
            raise WrongResultException()
        self.result = res

    def set_new_move(self, move: Move) -> None:
        """
        Set new move in this game.

        If player tries to move out of his order, WrongPlayerException() is raised.
        """
        if self.status != 'running':
            raise GameNotRunningException()
        if move.player_to_move == self.player_to_move():
            xo_app_stub.set_new_move(self.game_id, move.player_to_move, [move.square, move.vertical, move.horizontal])
        else:
            raise WrongPlayerException()

    def get_board(self) -> str:
        """
        Get board state.

        Board state represented as a string.
        """
        if self.status != 'running':
            raise GameNotRunningException()
        return xo_app_stub.get_board(self.game_id)

    def player_to_move(self) -> str:
        """
        Get player to move now.

        Returns one of strings: 'first' or 'second'.
        """
        if self.status != 'running':
            raise GameNotRunningException()
        return xo_app_stub.get_player_to_move(self.game_id)

    def is_finished(self) -> bool:
        """
        Check game ending by its internal rules.
        """
        if self.status != 'running':
            raise GameNotRunningException()
        return xo_app_stub.finished(self.game_id)

    def update_result(self) -> None:
        """
        Set result by rules of game.

        Result may be one of strings: 'first_win', 'second_win', 'draw', 'none'.
        """
        if self.status != 'running':
            raise GameNotRunningException()
        self.result = xo_app_stub.result(self.game_id)

    def get_result(self) -> str:
        """
        Get result of game.

        Result may be one of strings: 'first_win', 'second_win', 'draw', 'none'.
        """
        if self.status != 'running':
            raise GameNotRunningException()
        return self.result

    def get_win_pos(self) -> str:
        """
        Get winning sequence of squares.

        Win pos represented as a string.
        """
        if self.status != 'running':
            raise GameNotRunningException()
        return xo_app_stub.get_win_coords(self.game_id)

    def get_moves(self) -> str:
        """
        Get full notation of moves.

        Moves represented as a string.
        """
        if self.status != 'running':
            raise GameNotRunningException()
        return xo_app_stub.get_moves(self.game_id)


class PlaygroundException(Exception):
    def __init__(self):
        super().__init__()


class AlreadyRegistered(PlaygroundException):
    def __init__(self):
        super().__init__()


class NotRegistered(PlaygroundException):
    def __init__(self):
        super().__init__()


class AlreadyPlaying(PlaygroundException):
    def __init__(self):
        super().__init__()


class AlreadyWaiting(PlaygroundException):
    def __init__(self):
        super().__init__()


class NotIdleException(PlaygroundException):
    def __init__(self):
        super().__init__()


class NotWaitingException(PlaygroundException):
    def __init__(self):
        super().__init__()


class NoGameFoundException(PlaygroundException):
    def __init__(self):
        super().__init__()


class NotPlayingException(PlaygroundException):
    def __init__(self):
        super().__init__()


class Playground:
    """
    Class, responsible for players and games management.
    """
    def __init__(self):
        self.users = {}
        self.games = {}
        self.ready_list = set()
        self.playing_list = set()

    def register(self, user_id: str) -> None:
        """
        Create new player with a given user id.

        user_id must be unique. If not, AlreadyRegistered() exception is raised.
        """
        if self.is_registered(user_id):
            raise AlreadyRegistered()
        new_player = Player(user_id)
        self.users[user_id] = new_player

    def unregister(self, user_id: str) -> None:
        """
        Remove player with a given user id.

        Only applicable if the user already exists and is in 'idle' state.
        If not exists or in 'waiting' or 'playing' state an appropriate exception is raised.
        """
        if not self.is_registered(user_id):
            raise NotRegistered()
        if self.is_waiting(user_id) or self.is_playing(user_id):
            raise NotIdleException()
        self.users.pop(user_id)

    def is_registered(self, user_id: str) -> bool:
        """
        Check player existence by user id.
        """
        return user_id in self.users

    def is_waiting(self, user_id: str) -> bool:
        """
        Check if player with a given user id is in 'waiting' state.
        """
        return user_id in self.ready_list

    def is_playing(self, user_id: str) -> bool:
        """
        Check if player with a given user id is in 'playing' state.
        """
        return user_id in self.playing_list

    def add_entry(self, entry: Entry) -> None:
        """
        Add new entry with user preferences for a new game.

        Only applicable if user is registered and in an idle state.
        If not, the appropriate exception is raised.
        The user state becomes 'waiting'.
        """
        user_id = entry.user_id
        if not self.is_registered(user_id):
            raise NotRegistered()
        if self.is_waiting(user_id) or self.is_playing(user_id):
            raise NotIdleException()
        player = self.users[user_id]
        player.add_entry(entry)
        self.ready_list.add(user_id)

    def remove_entry(self, user_id: str) -> None:
        """
        Remove entry for a given user id.

        Applicable only in 'waiting' state. If not,
        NotWaitingException() is raised.
        """
        if self.is_waiting(user_id):
            player = self.users[user_id]
            player.remove_entry()
            self.ready_list.remove(user_id)
        else:
            raise NotWaitingException()

    def find_match(self, user_id: str) -> Optional[str]:
        """
        Find user that matches as an opponent for a given user id,
        according to submitted entries.

        Returns user id of the opponent or None if no match was found.
        If user is not in 'waiting' state, NotWaitingException() is raised.
        """
        if self.is_waiting(user_id):
            for uid in self.ready_list:
                if uid is not user_id:
                    if self.users[user_id].entry.match(self.users[uid].entry):
                        return uid
            return None
        else:
            raise NotWaitingException()

    def add_game(self, uid1: str, uid2: str) -> None:
        """
        Create new game with uid1 and uid2 as players ids.

        If one or both users are not in 'waiting' state, NotWaitingException() is raised.
        Both users transit to 'playing' state.
        """
        if self.is_waiting(uid1) and self.is_waiting(uid2):
            new_game = Game()
            new_game.setup(self.users[uid1].entry, self.users[uid2].entry)
            game_id = new_game.start()      # !!!!!
            player1, player2 = self.users[uid1], self.users[uid2]
            player1.add_game(new_game)
            player2.add_game(new_game)
            self.games[game_id] = new_game
            self.ready_list.remove(uid1)
            self.ready_list.remove(uid2)
            self.playing_list.add(uid1)
            self.playing_list.add(uid2)
        else:
            raise NotWaitingException()

    def remove_game(self, game_id: int) -> None:
        """
        Remove game with a given game id.

        Just removes instance of game and sets both users to 'idle' state.
        If game not found, raises NoGameFoundException()
        """
        if game_id in self.games:
            game = self.games[game_id]
            # todo call user.remove_game() in game.clear()
            for user_id in game.players.values():
                self.users[user_id].remove_game()
                self.playing_list.remove(user_id)
            game.clear()
            self.games.pop(game_id)
        else:
            raise NoGameFoundException()

    def side(self, user_id: str) -> str:
        """
        Return side of player with given user id.

        Player must be in 'playing' state.
        If not, raises NotPlayingException()
        """
        if not self.is_playing(user_id):
            raise NotPlayingException()
        return self.users[user_id].side

    def game_id(self, user_id: str) -> int:
        """
        Return id of game, played by player with given user id.

        Player must be in 'playing' state.
        If not, raises NotPlayingException()
        """
        if not self.is_playing(user_id):
            raise NotPlayingException()
        return self.users[user_id].game_id

    def opp_id(self, user_id: str) -> str:
        """
        Return opponent user id.

        Player must be in 'playing' state.
        If not, raises NotPlayingException()
        """
        if not self.is_playing(user_id):
            raise NotPlayingException()
        return self.users[user_id].opp_id

    def game(self, game_id: str) -> Game:
        """
        Return game instance with given game id.

        If no game with such id, raises NoGameFoundException()
        """
        if game_id not in self.games:
            raise NoGameFoundException()
        return self.games[game_id]
