active_players = {}


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
