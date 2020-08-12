import logging
import datetime

from discord.ext import commands


logger = logging.getLogger(__name__)
handler = logging.FileHandler('../logs/{}.log'.format(str(datetime.datetime.now()).replace(' ', '_').replace(':', 'h', 1).replace(':', 'm').split('.')[0][:-2]))
formatter = logging.Formatter('%(asctime)s::%(levelname)s::%(name)s::%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO)

logging.info("Starting \"Fully Automated Nutcracker\" bot script!")
_pfx = ["!"]
bot = commands.Bot(command_prefix=_pfx)
bot.help_command = commands.MinimalHelpCommand()
version = "v0.0.1b"

START_TIME = datetime.datetime.now()


@bot.event
async def on_ready():
    logger.info(f"Successfully logged into account {bot.user.name} with id {str(bot.user.id)} and version {version}")
