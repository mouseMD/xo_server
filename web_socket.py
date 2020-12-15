from aiohttp import web, WSMsgType
from aiohttp_security import authorized_userid
import players
from protocol import handle_command, handle_error
import json


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
                await handle_command(json.loads(msg.data), user_id, ws)
            elif msg.type == WSMsgType.ERROR:
                print('ws connection closed with exception %s' % ws.exception())
                await handle_error(user_id)

        print('websocket connection closed')

    return ws

