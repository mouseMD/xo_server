from aiohttp import web
import aiohttp_jinja2
from aiohttp_security import is_anonymous, remember, authorized_userid
from auth import get_new_anonymous_user_id


# decorator to autocreate temporary user ids for not autheticated usera
def auto_new_user(handler):
    async def wrap_handler(request):
        is_logged = not await is_anonymous(request)
        if is_logged:
            return await handler(request)
        else:
            user_id = "User#" + str(get_new_anonymous_user_id())
            redirect_response = web.HTTPFound(request.rel_url)
            await remember(request, redirect_response, user_id)
            raise redirect_response
    return wrap_handler


@aiohttp_jinja2.template('index.html')
@auto_new_user
async def index(request):
    user_id = await authorized_userid(request)
    return {'variable': user_id}


@aiohttp_jinja2.template('wait_game.html')
@auto_new_user
async def wait_game(request):
    user_id = await authorized_userid(request)
    return {'user': user_id}

