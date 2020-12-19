import xo_app_stub

active_players = {}


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


class Game:
    def __init__(self):
        self.game_id = None
        self.players = {}   # {"first" : uid1, "second" : uid2}
        self.status = "idle"
        self.game_type = None
        self.result = None

    def setup(self, entry1, entry2):
        self.game_type = entry1.game_type   # or entry2.game_type
        if entry1.side == "first" or entry2.side == "second":
            self.players = {"first" : entry1.user_id, "second": entry2.user_id}
        else:
            self.players = {"first": entry2.user_id, "second": entry1.user_id}

    def start(self):
        self.game_id = xo_app_stub.create_new_game()
        self.status = "running"
        return self.game_id

    def is_removable(self):
        return self.status == "idle"

    def clear(self):
        xo_app_stub.release_game(self.game_id)
        self.game_id = None
        self.players = {}
        self.status = "idle"
        self.game_type = None

    def first(self):
        return self.players["first"]

    def second(self):
        return self.players["second"]

    def set_result(self, res):
        self.result = res

    def set_new_move(self, move):
        if move.player_to_move == self.player_to_move():
            xo_app_stub.set_new_move(self.game_id, move.player_to_move, [move.square, move.vertical, move.horizontal])
        else:
            raise GameException()

    def get_board(self):
        return xo_app_stub.get_board(self.game_id)

    def player_to_move(self):
        return xo_app_stub.get_player_to_move(self.game_id)

    def is_finished(self):
        return xo_app_stub.finished(self.game_id)

    def get_result(self):
        if self.result is None:
            self.result = xo_app_stub.result(self.game_id)
        return self.result

    def get_win_pos(self):
        return xo_app_stub.get_win_coords(self.game_id)

    def get_moves(self):
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


class Playground:
    def __init__(self):
        self.users = {}
        self.games = {}
        self.ready_list = set()
        self.playing_list = set()

    def register(self, user_id):
        if self.is_registered(user_id):
            raise AlreadyRegistered()
        new_player = Player(user_id)
        self.users[user_id] = new_player

    def unregister(self, user_id):
        if not self.is_registered(user_id):
            raise PlaygroundException()
        if self.is_waiting(user_id) or self.is_playing(user_id):
            raise PlaygroundException()
        self.users.pop(user_id)

    def is_registered(self, user_id):
        return user_id in self.users

    def is_waiting(self, user_id):
        return user_id in self.ready_list

    def is_playing(self, user_id):
        return user_id in self.playing_list

    def add_entry(self, entry):
        user_id = entry.user_id
        if not self.is_registered(user_id):
            raise NotRegistered()
        if self.is_waiting(user_id) or self.is_playing(user_id):
            raise AlreadyPlaying()
        player = self.users[user_id]
        player.add_entry(entry)
        self.ready_list.add(user_id)

    def remove_entry(self, user_id):
        if self.is_waiting(user_id):
            player = self.users[user_id]
            player.remove_entry()
            self.ready_list.remove(user_id)
        else:
            raise PlaygroundException()

    def find_match(self, user_id):
        if self.is_waiting(user_id):
            for uid in self.ready_list:
                if uid is not user_id:
                    if self.users[user_id].entry.match(self.users[uid].entry):
                        return uid
            return None
        else:
            raise PlaygroundException()

    def add_game(self, uid1, uid2):
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
            raise PlaygroundException()

    def remove_game(self, game_id):
        if game_id in self.games:
            game = self.games[game_id]
            for user_id in game.players.values():
                self.users[user_id].remove_game()
                self.playing_list.remove(user_id)
            game.clear()
            self.games.pop(game_id)
        else:
            raise PlaygroundException()

    def side(self, user_id):
        return self.users[user_id].side

    def game_id(self, user_id):
        return self.users[user_id].game_id

    def opp_id(self, user_id):
        return self.users[user_id].opp_id

    def game(self, game_id):
        return self.games[game_id]


class ActivePlayer:
    def __init__(self, ws):
        self.ws = ws
        self.game_id = None
        self.opponent_id = None
        self.ptype = None

    def start_game(self, game_id, opponent_id, ptype):
        self.game_id = game_id
        self.opponent_id = opponent_id
        self.ptype = ptype

    def finish_game(self):
        self.game_id = None
        self.opponent_id = None
        self.ptype = None


waiting_list = []


async def get_suitable_opponent(criteria):
    return (waiting_list.pop()[0], 0) if waiting_list else None


async def add_to_waiting_list(user_id, criteria):
    waiting_list.append((user_id, criteria))

offers = []
