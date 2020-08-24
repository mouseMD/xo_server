from aiohttp_security.abc import AbstractAuthorizationPolicy


class MyAuthorizationPolicy(AbstractAuthorizationPolicy):
    async def authorized_userid(self, identity):
        return identity

    async def permits(self, identity, permission, context=None):
        return True


_global_user_counter = 0


def get_new_anonymous_user_id():
    global _global_user_counter
    _global_user_counter += 1
    return _global_user_counter
