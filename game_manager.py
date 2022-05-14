import xo_app_stub
# xo_app_stub should provide interface for only one game, not a collection


class GameManager:
    """
    Global state, responsible for all current games of particular kind
    All logic for storing entries, matching players and tracing active players is in another place
    """
    def __init__(self):
        self.games = {}
        self._last_used_id = 0

    def add_new_game(self, user1_id, user2_id):
        """
        Creates a new game instance, works as a factory.
        Responsible for providing the unique new id for a game
        :return: game unique id
        """
        new_id = self._get_unique_id()
        game = Game(new_id, user1_id, user2_id)
        self.games[new_id] = game
        return new_id

    def _get_unique_id(self):
        """
        Should be the safe way to get unique id
        :return:
        """
        self._last_used_id += 1
        return self._last_used_id

    def remove_game(self, game_id):
        del self.games[game_id]


class Game:
    """
    Wraps game state.
    """
    def __init__(self, game_id, user1_id, user2_id):
        self.id = game_id           # do we need it?
        self.xo_app_game = None     # will point to actual implementation
        self.completed = False       # use for communicating game completion to clients
        self.draw_offered = False
        self.player_to_move_next = user1_id
        self.player1 = user1_id
        self.player2 = user2_id
        self.watchers = set()
        self.last_move = None
        self.notation = None        # full list of moves
        self.winning_combination = None

    def is_allowed_move(self) -> bool:
        """
        check if the passed move is allowed by rules of game
        :return:
        """
        return False

    def apply_move(self):
        pass

    def update_state_by_rules(self):
        """
        update state of game after passing last move to game engine
        :return:
        """
        pass

    def get_watchers_list(self):
        return self.watchers

    def add_new_watcher(self, user_id):
        pass

    def remove_watcher(self, user_id):
        pass
