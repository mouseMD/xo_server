import asyncio
from aiohttp import web
from routes import setup_routes

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    app = web.Application()
    setup_routes(app)
    web.run_app(app)