from players import Playground, Matcher
global_playground = Playground(Matcher())
global_sockets = {}


class SocketRegistry:
    """
    Registry for all user sockets
    """
    sockets = {}

    def get_socket(self, user_id):
        return self.sockets[user_id]

    def add_socket(self, user_id, ws):
        self.sockets[user_id] = ws

    def remove_socket(self, user_id):
        self.sockets.pop(user_id, None)
