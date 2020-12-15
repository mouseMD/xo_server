from aiohttp import web, WSMsgType
from aiohttp_security import authorized_userid
import players
from protocol import handle_command, handle_error
import json
import logging


async def websocket_handler(request):
    ws = web.WebSocketResponse()
    try:
        await ws.prepare(request)
    except web.HTTPException as e:
        logging.info('Failed to open WebSocket')
    else:
        user_id = await authorized_userid(request)
        logging.info("websocket connection opened with user_id {}".format(user_id))
        # if already connected, not permit connection
        if user_id in players.active_players:
            logging.info("Deliberately closed connection with already connected user_id {}!".format(user_id))
            await ws.close()
        else:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    await handle_command(json.loads(msg.data), user_id, ws)
                elif msg.type == WSMsgType.ERROR:
                    logging.info('connection closed with exception {} with user_id {}'.format(ws.exception(), user_id))
                    await handle_error(user_id)

            logging.info('websocket connection closed with user_id {}'.format(user_id))

    return ws

