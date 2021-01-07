import time
from aiohttp_security.abc import AbstractAuthorizationPolicy


class MyAuthorizationPolicy(AbstractAuthorizationPolicy):
    async def authorized_userid(self, identity):
        return identity

    async def permits(self, identity, permission, context=None):
        return True


def get_new_anonymous_user_id():
    return time.time()
