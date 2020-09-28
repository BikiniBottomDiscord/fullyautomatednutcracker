from discord.ext import commands
from utils import common

bot = commands.Bot(command_prefix='%%')
bot.remove_command('help')


@bot.event
async def on_ready():
    print('Successfully logged into account ' + str(bot.user.name) + ' with id ' + str(bot.user.id))
    channel = 742559349750235136
    total = 0
    messages = []
    print(f"Inspecting channel {channel} a.k.a {bot.get_channel(channel).name}")
    async for message in bot.get_channel(channel).history(limit=None):
        total += 1
        if message.content and message.content != "":
            messages.append((message.guild.id, message.channel.id, message.id, message.author.id, str(message.created_at), message.content))
        if total % 50000 == 0:
            print(f"\r{total:,} processed...")
    print(f"\r{total:,} processed...")
    print("Saving to file.")
    with open(f"{channel}.log", "w", encoding='utf8') as fp:
        for gid, cid, mid, aid, ivt, msg in messages:
            try:
                fp.write(f"{gid},{cid},{mid},{aid},{ivt},{msg}\n")
            except:
                print("could not save: " + msg)
    print("Done.")
    await bot.close()

bot.run(common.load_creds(False, common.EcosystemBots.FullyAutomatedNutcracker))
