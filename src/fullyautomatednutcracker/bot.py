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
version = "v0.1.0b"

START_TIME = datetime.datetime.now()
STARTED = False


@bot.event
async def on_ready():
    global STARTED
    logger.info(f"Successfully logged into account {bot.user.name} with id {str(bot.user.id)} and version {version}")
    await bot.change_presence(activity=discord.Activity(name="nuts and bananas", type=discord.ActivityType.watching))
    bot.version = version
    bot.start_time = START_TIME
    if not STARTED:
        await bot.load_extension("fullyautomatednutcracker.manager")
        await bot.fetch_guild(Settings.instance.GUILD)
        loaded, total = await bot.get_cog("Manager").load_all_cogs()
        STARTED = True
        common.load_blacklist()
        await bot.get_channel(Settings.instance.TREEDOME).send(f"Fully Automated Nutcracker is online.\nLoaded {loaded} of {total} available cogs.")


@bot.event
async def on_message(message):
    # if not message.guild:  # with this here, commands won't work in DM.
    #     return
    if message.channel.id != Settings.instance.JELLYFISH_FIELDS or common.is_admin(message.author):  # disables commands in jellyfish fields for non-mods
        await bot.process_commands(message)


@bot.event
async def on_command_error(context, exception):
    for _class in [commands.CommandNotFound, commands.CheckFailure]:
        if isinstance(exception, _class):
            return
    for _class in [commands.MissingRequiredArgument]:
        if isinstance(exception, _class):
            await context.send_help(context.command)
            return
    exc = traceback.format_exception(exception.__class__, exception, exception.__traceback__)
    exc = ''.join(exc) if isinstance(exc, list) else exc
    logger.error(f'Ignoring exception in command {context.command}:\n{exc}')
