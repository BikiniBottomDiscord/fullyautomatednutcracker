import asyncio
import sys

from utils import common
from fullyautomatednutcracker import bot as fan_bot
from utils import global_guild_settings

DEBUG_MODE = not (len(sys.argv) == 2 and sys.argv[1] == "prod")
common.load_admins()
ggs = global_guild_settings.BotGuildSettings(
    DEBUG_MODE,
    None,
    fan_bot.bot
)


async def get_bots():
    fullyautomatednutcrackerbot = fan_bot.bot.start(common.load_creds(DEBUG_MODE, common.EcosystemBots.FullyAutomatedNutcracker))
    return await asyncio.gather(*(fullyautomatednutcrackerbot,))
asyncio.run(get_bots())
