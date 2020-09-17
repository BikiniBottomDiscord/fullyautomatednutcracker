from discord.ext import commands
import asyncio

import time



class AntiSelfDeprecation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.nono_words = []
        self.dumb = ('im dumb', 'i\'m dumb', 'im stupid', 'i\'m stupid')
        self.not_dumb = ('im not dumb', 'i\'m not dumb', 'i\'m not stupid', 'im not stupid')
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

    # bump timer, waits 2 hours and 30 minutes
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == 302050872383242240 and len(message.embeds) > 0 and 'Bump done' in message.embeds[0].description:
            bumped = time.monotonic()
            self.last_bumped = bumped
            await message.add_reaction(':thumbsup:')
            await asyncio.sleep(9000)
            if self.last_bumped == bumped:
                await message.channel.send('<a:filterfeed:693001359934357563> No one\'s bumped our server in over two hours! Disboard keeps us up on the front page! Use `!d bump` to bump us!')

def setup(bot):
    bot.add_cog(AntiSelfDeprecation(bot))
