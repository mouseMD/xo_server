import xo_app_stub
from typing import Optional, Iterable


class Entry:
    def __init__(self, player: 'Player', params: dict) -> None:
        self.player = player
        self.game_type = None
        self.side = None
        self.requested_user_id = None
        self.entry_type = None  # broadcast, bot, user


class Player:
    """
    Incapsulates information about player.

    Player can be in one of three states: idle, waiting, playing.
    Starts always in 'idle' state.
    In waiting state contains reference to entry. Enters in this state by calling
    'add_entry' and exits by calling 'remove_entry()' or 'add_game()'.
    In playing state contains reference to game and caches info about side and opponent.
    Enters in this state by calling 'add_game()' and exits by calling 'remove_game()'.
    """
    def __init__(self, player_id: str) -> None:
        self.player_id = player_id
        self.status = "idle"
        # for waiting state
        self.entry = None
        # for playing state
        self.game = None
        self.side = None
        self.opp = None

    def add_entry(self, entry: Entry) -> None:
        """
        Move to 'waiting' state with entry.
        """
        self.entry = entry
        self.status = "waiting"

    def remove_entry(self) -> None:
        """
        Remove entry and transit to 'idle' state.
        """
        self.entry = None
        self.status = "idle"

    def add_game(self, game: 'Game') -> None:
        """
        Move to 'playing' state with game.
        """
        self.game = game
        if self is game.first():
            self.side = "first"
            self.opp = game.second()
        else:
            self.side = "second"
            self.opp = game.first()
        self.entry = None
        self.status = "playing"

    def remove_game(self) -> None:
        """
        Remove entry and transit to 'idle' state.
        """
        self.game = None
        self.side = None
        self.status = "idle"
        self.opp = None

    def is_idle(self) -> bool:
        return self.status == "idle"

    def is_waiting(self) -> bool:
        return self.status == "waiting"

    def is_playing(self) -> bool:
        return self.status == "playing"


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
    def create_move(ptm, sq, ver, hor):
        m = Move()
        m.square = sq
        m.vertical = ver
        m.horizontal = hor
        m.player_to_move = ptm
        return m


class Match:
    def __init__(self, player1: Player, player2: Player, game_type: str) -> None:
        self.first_player = player1
        self.second_player = player2
        self.game_type = game_type


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
    def __init__(self) -> None:
        self.game_id = None
        self.first_player = None
        self.second_player = None
        self.status = "idle"
        self.game_type = None
        self.result = 'none'

    def setup(self, match: Match) -> None:
        """
        Setup game state before starting actual play based on found match.

        If called when game is in 'running' state, raises GameAlreadyRunnningException().
        """
        if self.status == "idle":
            self.status = "ready"
            self.game_type = match.game_type
            self.first_player = match.first_player
            self.second_player = match.second_player
            self.first_player.add_game(self)
            self.second_player.add_game(self)
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
        self.first_player.remove_game()
        self.second_player.remove_game()
        self.first_player = None
        self.second_player = None
        self.status = "idle"
        self.game_type = None

    def first(self) -> Player:
        """
        Return the first player.

        Game must be in 'ready' or 'running' state, else GameNotReadyException() is raised.
        """
        if self.status == 'idle':
            raise GameNotReadyException()
        return self.first_player

    def second(self) -> Player:
        """
        Return the second player.

        Game must be in 'ready' or 'running' state, else GameNotReadyException() is raised.
        """
        if self.status == 'idle':
            raise GameNotReadyException()
        return self.second_player

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
        print(move.player_to_move)
        print(self.player_to_move())
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


class Matcher:
    def __init__(self):
        self.type = 1

    def match(self, entry: Entry, es: Iterable[Entry]) -> Optional[Match]:
        if self.type == 1:
            for e in es:
                if e is not entry:
                    return Match(e.player, entry.player, e.game_type)
        return None


class Playground:
    """
    Class, responsible for players and games management.
    """
    def __init__(self, matcher: Matcher) -> None:
        self.users = {}
        self.ready_list = set()
        self.matcher = matcher

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
        player = self.users[user_id]
        if player.is_waiting() or player.is_playing():
            raise NotIdleException()
        self.users.pop(user_id)

    def is_registered(self, user_id: str) -> bool:
        """
        Check player existence by user id.
        """
        return user_id in self.users

    def add_entry(self, entry: Entry) -> None:
        """
        Add new entry with user preferences for a new game.

        Only applicable if user is in an idle state.
        If not, the appropriate exception is raised.
        The user state becomes 'waiting'.
        """
        player = entry.player
        if player.is_waiting() or player.is_playing():
            raise NotIdleException()
        player.add_entry(entry)
        self.ready_list.add(entry)

    def remove_entry(self, user_id: str) -> None:
        """
        Remove entry for a given user id.

        Applicable only in 'waiting' state. If not,
        NotWaitingException() is raised.
        """
        player = self.users[user_id]
        if player.is_waiting():
            self.ready_list.remove(player.entry)
            player.remove_entry()
        else:
            raise NotWaitingException()

    def find_match(self, entry: Entry) -> Optional[Match]:
        """
        Find user that matches as an opponent for a player,
        according to submitted entries.

        Returns user id of the opponent or None if no match was found.
        If user is not in 'waiting' state, NotWaitingException() is raised.
        """
        return self.matcher.match(entry, self.ready_list)

    def add_game(self, match: Match) -> Game:
        """
        Create new game with uid1 and uid2 as players ids.

        If one or both users are not in 'waiting' state, NotWaitingException() is raised.
        Both users transit to 'playing' state.
        """
        player1 = match.first_player
        player2 = match.second_player
        if player1.is_waiting() and player2.is_waiting():
            self.ready_list.remove(player1.entry)
            self.ready_list.remove(player2.entry)
            new_game = Game()
            new_game.setup(match)
            new_game.start()
            return new_game
        else:
            raise NotWaitingException()

    def player(self, user_id: str) -> Player:
        """
        Return player instance by user id.

        Raises NotRegistered() if no such user found.
        """
        if user_id not in self.users:
            raise NotRegistered()
        return self.users[user_id]
