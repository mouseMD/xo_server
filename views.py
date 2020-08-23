from aiohttp import web, WSMsgType
import aiohttp_jinja2
from aiohttp_security import is_anonymous, remember, forget, authorized_userid


@aiohttp_jinja2.template('index.html')
async def index(request):
    is_logged = not await is_anonymous(request)
    if is_logged:
        user_id = await authorized_userid(request)
        return {'variable': user_id}
    else:
        user_id = "Unathorized user"
        redirect_response = web.HTTPFound('/')
        await remember(request, redirect_response, user_id)
        raise redirect_response


async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    user_id = await authorized_userid(request)
    async for msg in ws:
        if msg.type == WSMsgType.TEXT:
            if msg.data == 'close':
                await ws.close()
            else:
                await ws.send_str(msg.data + user_id)
        elif msg.type == WSMsgType.ERROR:
            print('ws connection closed with exception %s' % ws.exception())

    print('websocket connection closed')

    return ws
