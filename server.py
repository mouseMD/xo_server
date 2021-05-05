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
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker


async def create_connection(app):
    DB_URL = "postgresql+asyncpg://user:user@localhost/xo_db"
    engine = create_async_engine(DB_URL, echo=True)
    app['db'] = engine
    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    app['session'] = async_session()


async def delete_connection(app):
    await app['session'].close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M')
    loop = asyncio.get_event_loop()
    middleware = session_middleware(EncryptedCookieStorage(b'Thirty two length bytes key.    '))
    app = web.Application(middlewares=[middleware])
    aiohttp_jinja2.setup(app,
                         loader=jinja2.FileSystemLoader(str(BASE_DIR / 'templates')))
    setup_routes(app)
    setup_static_routes(app)
    setup_security(app, SessionIdentityPolicy(), MyAuthorizationPolicy())
    app.on_startup.append(create_connection)
    app.on_cleanup.append(delete_connection)
    web.run_app(app)
