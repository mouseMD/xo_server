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
    def from_params(self, params):
        pass

    def match(self, entry):
        return True


class Player:
    def __init__(self, player_id):
        self.player_id = player_id
        self.game_id = None
        self.side = None
        self.entry = None
        self.status = "idle"

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
        self.entry = None
        self.status = "playing"

    def remove_game(self):
        self.game_id = None
        self.side = None
        self.status = "idle"


class ConnectedPlayer(Player):
    def __init__(self, player_id, ws):
        super().__init__(player_id)
        self.ws = ws


class Game:
    def __init__(self):
        self.game_id = None
        self.players = {}   # {"first" : uid1, "second" : uid2}
        self.status = "idle"
        self.game_type = None

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


class PlaygroundException(Exception):
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
            raise PlaygroundException()
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
            raise PlaygroundException()
        if self.is_waiting(user_id) or self.is_playing(user_id):
            raise PlaygroundException()
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
        else:
            raise PlaygroundException()

    def remove_game(self, game_id):
        if game_id in self.games:
            game = self.games[game_id]
            for user_id in game.players.values():
                self.users[user_id].remove_game()
            game.clear()
            self.games.pop(game_id)
        else:
            raise PlaygroundException()


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
