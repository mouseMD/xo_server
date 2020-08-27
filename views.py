from aiohttp import web, WSMsgType
import aiohttp_jinja2
from aiohttp_security import is_anonymous, remember, forget, authorized_userid
from auth import get_new_anonymous_user_id
import players
from protocol import handle_command, handle_error


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


async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    user_id = await authorized_userid(request)
    # if already connected, not permit connection
    if user_id in players.active_players:
        await ws.close()
    else:
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                await handle_command(msg.data, user_id, ws)
            elif msg.type == WSMsgType.ERROR:
                print('ws connection closed with exception %s' % ws.exception())
                await handle_error(user_id)

        print('websocket connection closed')

    return ws


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
