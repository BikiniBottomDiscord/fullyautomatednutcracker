import discord
import logging
import datetime
import traceback

from discord.ext import commands
from os import listdir
from os.path import join, isfile

from utils.global_guild_settings import BotGuildSettings as Settings


logger = logging.getLogger(__name__)
handler = logging.FileHandler('../logs/{}.log'.format(str(datetime.datetime.now()).replace(' ', '_').replace(':', 'h', 1).replace(':', 'm').split('.')[0][:-2]))
formatter = logging.Formatter('%(asctime)s::%(levelname)s::%(name)s::%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO)

logging.info("Starting \"Fully Automated Nutcracker\" bot script!")
_pfx = ["$", "dmb ", "<:daddy:590058725252005888> "]
bot = commands.Bot(command_prefix=_pfx)
bot.help_command = commands.MinimalHelpCommand()
# bot.is_owner = is_owner  # TODO: do we want this? @dove
version = "v0.0.1b"

START_TIME = datetime.datetime.now()
STARTED = False


@bot.event
async def on_ready():
    logger.info(f"Successfully logged into account {bot.user.name} with id {str(bot.user.id)} and version {version}")
    global STARTED
    if not STARTED:
        await bot.get_channel(Settings.instance.TREEDOME).send(f"Starting up...")
        STARTED = True


cog_dir = "fullyautomatednutcracker/cogs"
import_dir = cog_dir.replace('/', '.')
COGS_LOADED = False
if not COGS_LOADED:
    for extension in [f.replace('.py', '') for f in listdir(cog_dir) if isfile(join(cog_dir, f))]:
        try:
            bot.load_extension(import_dir + "." + extension)
            print(f'Successfully loaded extension {extension}.')
        except (discord.ClientException, ModuleNotFoundError):
            print(f'Failed to load extension {extension}.')
            traceback.print_exc()
    COGS_LOADED = True
