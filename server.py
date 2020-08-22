import asyncio
from aiohttp import web
from routes import setup_routes, setup_static_routes
import aiohttp_jinja2
import jinja2
from settings import BASE_DIR

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    app = web.Application()
    aiohttp_jinja2.setup(app,
                         loader=jinja2.FileSystemLoader(str(BASE_DIR / 'templates')))
    print(str(BASE_DIR / 'templates'))
    setup_routes(app)
    setup_static_routes(app)
    web.run_app(app)
