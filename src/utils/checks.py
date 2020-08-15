
from discord.ext import commands

from utils.common import is_admin as _common_admin


async def is_owner(user):
    return _common_admin(user)


def is_admin():
    async def pred(ctx):
        return _common_admin(ctx.author)
    return commands.check(pred)


