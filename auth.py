import time
from aiohttp_security.abc import AbstractAuthorizationPolicy
from models import User
from sqlalchemy import select


class MyAuthorizationPolicy(AbstractAuthorizationPolicy):

    def __init__(self, app):
        self._app = app
        super().__init__()

    async def authorized_userid(self, identity):
        if not identity.startswith('auth'):
            return None
        else:
            # go to db for authorization
            login = identity[5:]
            session = self._app['session']
            stmt = select(User).where(User.login == login)
            async with session.begin():
                result = await session.execute(stmt)
                users = result.scalars().all()
                if users:
                    users[0].ping()
                else:
                    login = None
            return login

    async def permits(self, identity, permission, context=None):
        return True


def get_new_anonymous_user_id():
    return time.time()
