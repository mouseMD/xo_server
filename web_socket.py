from aiohttp import web, WSMsgType
from aiohttp_security import authorized_userid
from players import AlreadyRegistered
from protocol import handle_command, handle_error, send_command
from commands import ErrorCommand
import json
import logging
from global_defs import global_playground, registry


async def websocket_handler(request):
    ws = web.WebSocketResponse()
    try:
        await ws.prepare(request)
    except web.HTTPException:
        logging.info('Failed to open WebSocket')
    else:
        await process_connection(ws, request)
    return ws


async def process_connection(ws, request):
    user_id = await authorize_new_user(request)
    logging.info("websocket connection opened with user_id {}".format(user_id))
    try:
        register_new_user(user_id)
    except NotPermittedUserException as e:
        await exit_connection(ws, user_id, e)
    else:
        register_socket(ws, user_id)
        await process_messages(ws, user_id)


async def authorize_new_user(request):
    return await authorized_userid(request)


def register_socket(ws, user_id):
    registry.add_socket(user_id, ws)


def register_new_user(user_id):
    try:
        global_playground.register(user_id)
    except AlreadyRegistered:
        raise NotPermittedUserException("User already registered")


async def exit_connection(ws, user_id, ex):
    error_message = "Deliberately closed connection with user_id {}! Reason: ".format(user_id) + ex.msg
    logging.info(error_message)
    await send_command(ErrorCommand(user_id, msg=error_message))
    await ws.close()


async def process_messages(ws, user_id):
    async for msg in ws:
        if msg.type == WSMsgType.TEXT:
            await handle_command(json.loads(msg.data), user_id)
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


class NotPermittedUserException(Exception):
    def __init__(self, msg):
        super().__init__()
        self.msg = msg
