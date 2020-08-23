from aiohttp_security.abc import AbstractAuthorizationPolicy


class MyAuthorizationPolicy(AbstractAuthorizationPolicy):
    async def authorized_userid(self, identity):
        return identity

    async def permits(self, identity, permission, context=None):
        return True

