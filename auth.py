import time
from aiohttp_security.abc import AbstractAuthorizationPolicy


class MyAuthorizationPolicy(AbstractAuthorizationPolicy):
    async def authorized_userid(self, identity):
        if not identity.startswith('auth'):
            return None
        else:
            # go to db for authorization
            return identity[5:]     # chop auth_ from the beginning

    async def permits(self, identity, permission, context=None):
        return True


def get_new_anonymous_user_id():
    return time.time()
