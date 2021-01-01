from aiohttp import web, WSMsgType
from aiohttp_security import authorized_userid
from players import AlreadyRegistered
from protocol import handle_command, handle_error, construct_error
import json
import logging
from global_defs import global_playground, global_sockets


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
        try:
            global_playground.register(user_id)
        except AlreadyRegistered:
            logging.info("Deliberately closed connection with already connected user_id {}!".format(user_id))
            await ws.send_json(await construct_error('User id {} already in use'.format(user_id)))
            await ws.close()
        else:
            global_sockets[user_id] = ws
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    await handle_command(json.loads(msg.data), user_id, ws)
                elif msg.type == WSMsgType.ERROR:
                    logging.info('connection closed with exception {} with user_id {}'.format(ws.exception(), user_id))
                    await handle_error(user_id)
                elif msg.type == WSMsgType.BINARY:
                    logging.info('Received BINARY type message')
                elif msg.type == WSMsgType.CLOSE:
                    logging.info('Received CLOSE type message')
                elif msg.type == WSMsgType.CLOSED:
                    logging.info('Received CLOSED type message')
                elif msg.type == WSMsgType.CLOSING:
                    logging.info('Received CLOSING type message')
                elif msg.type == WSMsgType.CONTINUATION:
                    logging.info('Received CONTINUATION type message')
                elif msg.type == WSMsgType.PING:
                    logging.info('Received PING type message')
                elif msg.type == WSMsgType.PONG:
                    logging.info('Received PONG type message')

            logging.info('websocket connection closed with user_id {}'.format(user_id))
            await handle_error(user_id)
    return ws
