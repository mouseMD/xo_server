import asyncio
from aiohttp import web
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from aiohttp_session import session_middleware
from aiohttp_security import setup as setup_security, SessionIdentityPolicy
import aiohttp_jinja2
import jinja2
from routes import setup_routes, setup_static_routes
from settings import BASE_DIR
from auth import MyAuthorizationPolicy


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    middleware = session_middleware(EncryptedCookieStorage(b'Thirty two length bytes key.    '))
    app = web.Application(middlewares=[middleware])
    aiohttp_jinja2.setup(app,
                         loader=jinja2.FileSystemLoader(str(BASE_DIR / 'templates')))
    setup_routes(app)
    setup_static_routes(app)
    setup_security(app, SessionIdentityPolicy(), MyAuthorizationPolicy())
    web.run_app(app)
