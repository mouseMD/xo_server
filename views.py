from aiohttp import web
import aiohttp_jinja2
from aiohttp_security import is_anonymous, remember, authorized_userid
from auth import get_new_anonymous_user_id
from functools import wraps
from models import User, UserException
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select


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
    authorized = (user_id is not None)
    return {'variable': user_id, 'auth': authorized}


@aiohttp_jinja2.template('wait_game.html')
async def wait_game(request):
    user_id = await authorized_userid(request)
    if user_id is None:
        raise web.HTTPForbidden()
    return {'user': user_id, 'variable': user_id, 'auth': True}


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
    session = request.app['session']
    try:
        async with session.begin():
            session.add(user)
    except IntegrityError:
        raise web.HTTPBadRequest(text='User already exists!')
    # create new identity for current user
    redirect_response = web.HTTPFound('/')
    identity = 'auth_' + login
    await remember(request, redirect_response, identity)

    # redirect to main page
    return redirect_response


async def login_user(request):
    """
    Login user.
    """
    # get user credentials
    data = await request.post()
    login = data['login']
    password = data['password']

    # here we have an old identity, we will change it to new if login successful
    session = request.app['session']
    stmt = select(User).where(User.login == login)
    result = await session.execute(stmt)
    users = result.scalars().all()
    if users and users[0].check_password(password):
        # create new identity
        identity = 'auth_' + login
        redirect_response = web.HTTPFound('/')
        await remember(request, redirect_response, identity)
    else:
        # redirect back
        redirect_response = web.HTTPFound('/')
    return redirect_response


async def logout_user(request):
    identity = "Anon_" + str(get_new_anonymous_user_id())
    redirect_response = web.HTTPFound('/')
    await remember(request, redirect_response, identity)
    raise redirect_response

