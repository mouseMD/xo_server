from aiohttp import web
import aiohttp_jinja2
from aiohttp_security import is_anonymous, remember, authorized_userid
from auth import get_new_anonymous_user_id
from functools import wraps
from models import User, UserException


# decorator to autocreate temporary user ids for not autheticated usera
def auto_new_user(handler):
    @wraps(handler)
    async def wrap_handler(request):
        is_logged = not await is_anonymous(request)
        if is_logged:
            return await handler(request)
        else:
            identity = "Anon_" + str(get_new_anonymous_user_id())
            redirect_response = web.HTTPFound(request.rel_url)
            await remember(request, redirect_response, identity)
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


async def add_new_user(request):
    """
    Register a new user.
    """
    # get user credentials
    data = await request.post()
    login = data['login']
    password = data['password']

    # create new user in database
    user = User.create_new(login, password)
    session = request.app.session
    async with session.begin():
        if User.query.filter_by(login=login).first() is not None:
            raise web.HTTPBadRequest(text="User already exists")
        session.add(user)

    # create new identity for current user
    redirect_response = web.HTTPFound(request.rel_url)
    identity = 'auth_' + login
    await remember(request, redirect_response, identity)

    # redirect to main page
    return redirect_response
