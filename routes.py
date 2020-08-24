from views import index, websocket_handler, wait_game
from settings import BASE_DIR


def setup_routes(app):
    app.router.add_get('/', index)
    app.router.add_get('/wait_game', wait_game)
    app.router.add_get('/ws', websocket_handler)


def setup_static_routes(app):
    app.router.add_static('/static/',
                          path=BASE_DIR / 'static',
                          name='static')
