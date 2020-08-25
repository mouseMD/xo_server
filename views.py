from aiohttp import web, WSMsgType
import aiohttp_jinja2
from aiohttp_security import is_anonymous, remember, forget, authorized_userid
from auth import get_new_anonymous_user_id
import players


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
    if user_id in players.players:
        await ws.close()
    else:
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                if msg.data == 'resign':
                    # remove active player and stop game if exists
                    player = players.players.pop(user_id)
                    if player.game_id is not None:
                        opp = players.players.pop(player.opponent_id)
                        await ws.send_str("end_game")
                        await opp.ws.send_str("end_game")
                        # save game to db
                        # remove game from app
                        await opp.ws.close()
                    await ws.close()
                elif msg.data == 'ready':
                    # add new active player
                    player = players.ActivePlayer(ws)
                    players.players[user_id] = player
                    # check if exist suitable opponent and create new game
                    opp_id = players.get_suitable_opponent({})
                    if opp_id is not None:
                        # create new game in app
                        game_id = 0
                        opponent = players.players[opp_id]
                        opponent.start_game(game_id, user_id)
                        player.start_game(game_id, opp_id)
                        await ws.send_str("started")
                        await opponent.ws.send_str("started")
                elif msg.data == 'move':
                    player = players.players[user_id]
                    opponent = players.players[player.opponent_id]
                    # update game
                    await ws.send_str("update_state")
                    await opponent.ws.send_str("update_state")
                    # check for game over
                    if False:
                        await ws.send_str("end_game")
                        await opponent.ws.send_str("end_game")
                        # save game to db
                        # remove game from app
                        await opponent.ws.close()
                        await ws.close()
                elif msg.data == 'offer':
                    pass
                    # here check for offer and answer and then end game as in "move"

            elif msg.type == WSMsgType.ERROR:
                print('ws connection closed with exception %s' % ws.exception())
                # remove active player and stop game if exists
                player = players.players.pop(user_id)
                if player.game_id is not None:
                    opp = players.players.pop(player.opponent_id)
                    await opp.ws.send_str("end_game")
                    # save game to db
                    # remove game from app
                    await opp.ws.close()

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
