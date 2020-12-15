from aiohttp import web, WSMsgType
import aiohttp_jinja2
from aiohttp_security import is_anonymous, remember, forget, authorized_userid
from auth import get_new_anonymous_user_id


@aiohttp_jinja2.template('index.html')
async def index(request):
    is_logged = not await is_anonymous(request)
    if is_logged:
        user_id = await authorized_userid(request)
        return {'variable': user_id}
    else:
        user_id = "User#" + str(get_new_anonymous_user_id())
        redirect_response = web.HTTPFound('/')
        await remember(request, redirect_response, user_id)
        raise redirect_response


@aiohttp_jinja2.template('wait_game.html')
async def wait_game(request):
    is_logged = not await is_anonymous(request)
    if is_logged:
        user_id = await authorized_userid(request)
        return {'user': user_id}
    else:
        user_id = "User#" + str(get_new_anonymous_user_id())
        redirect_response = web.HTTPFound('/wait_game')
        await remember(request, redirect_response, user_id)
        raise redirect_response
