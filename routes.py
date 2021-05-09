from views import index, wait_game, add_new_user, login_user, logout_user, get_active_users
from web_socket import websocket_handler
from settings import BASE_DIR


def setup_routes(app):
    app.router.add_get('/', index)
    app.router.add_get('/wait_game', wait_game)
    app.router.add_get('/ws', websocket_handler)
    app.router.add_post('/users', add_new_user)
    app.router.add_post('/login', login_user)
    app.router.add_post('/logout', logout_user)
    app.router.add_get('/users', get_active_users)


def setup_static_routes(app):
    app.router.add_static('/static/',
                          path=BASE_DIR / 'static',
                          name='static')
