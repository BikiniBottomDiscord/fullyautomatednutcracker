from discord.ext import commands
import asyncio


class AntiSelfDeprecation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.nono_words = []
        self.dumb = ('im dumb', 'i\'m dumb', 'im stupid', 'i\'m dumb')
        self.not_dumb = ('im not dumb', 'i\'m not dumb')
        self.bot.deny = ['shut', 'shut up', 'up shut']

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content.lower() in self.bot.nono_words:
            await message.channel.send("You're a good person and can't change my mind smh")
        elif message.content.lower().startswith(self.dumb):
            await message.channel.send('You\'re not dumb, you\'re learning')
            try:
                m = await self.bot.wait_for('message', check=lambda msg: msg.author.id == message.author.id and msg.channel == message.channel and msg.content.lower() in self.bot.deny, timeout=10.0)
                await m.channel.send('no u')
            except asyncio.TimeoutError:
                return
        elif message.content.lower().startswith(self.not_dumb):
            await message.channel.send('Correct.')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content.lower() == 'yoshi man good':
            await message.add_reaction('\U0001F49A')

def setup(bot):
    bot.add_cog(AntiSelfDeprecation(bot))
