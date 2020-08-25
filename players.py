players = {}


class ActivePlayer:
    def __init__(self, ws):
        self.ws = ws
        self.game_id = None
        self.opponent_id = None

    def start_game(self, game_id, opponent_id):
        self.game_id = game_id
        self.opponent_id = opponent_id

    def finish_game(self):
        self.game_id = None
        self.opponent_id = None


waiting_list = []


def get_suitable_opponent(criteria):
    return waiting_list.pop() if waiting_list else None


def add_to_waiting_list(user_id, criteria):
    waiting_list.append(user_id)
