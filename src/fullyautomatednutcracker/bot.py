import discord
import logging
import datetime
import traceback

from discord.ext import commands
from os import listdir
from os.path import join, isfile

from utils.global_guild_settings import BotGuildSettings as Settings
from utils.communityhelpcommand import CommunityHelpCommand
from utils import common


logger = logging.getLogger(__name__)
handler = logging.FileHandler('../logs/{}.log'.format(str(datetime.datetime.now()).replace(' ', '_').replace(':', 'h', 1).replace(':', 'm').split('.')[0][:-2]))
formatter = logging.Formatter('%(asctime)s::%(levelname)s::%(name)s::%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO)

logging.info("Starting \"Fully Automated Nutcracker\" bot script!")
_pfx = ["$", "dmb ", "<:daddy:590058725252005888> "]
bot = commands.Bot(command_prefix=_pfx, intents=discord.Intents.all(), case_insensitive=True)
bot.help_command = CommunityHelpCommand()
# bot.is_owner = is_owner  # TODO: do we want this? @dove
version = "v0.0.1b"

START_TIME = datetime.datetime.now()
STARTED = False


@bot.event
async def on_ready():
    logger.info(f"Successfully logged into account {bot.user.name} with id {str(bot.user.id)} and version {version}")
    global STARTED
    if not STARTED:
        common.load_blacklist()
        await bot.get_channel(Settings.instance.TREEDOME).send(f"Starting up...")
        STARTED = True
        

@bot.event
async def on_message(message):
    # if not message.guild:  # with this here, commands won't work in DM.
    #     return
    if message.channel.id != Settings.instance.JELLYFISH_FIELDS or common.is_admin(message.author):  # disables commands in jellyfish fields for non-mods
        await bot.process_commands(message)


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
