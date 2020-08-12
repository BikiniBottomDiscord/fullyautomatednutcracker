from discord.ext import commands


class AntiSelfDeprecation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.nono_words = []

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content.lower() in self.bot.nono_words:
            await message.channel.send("You're a good person and can't change my mind smh")
        elif message.content.lower().startswith(('im dumb', 'i\'m dumb')):
            await message.channel.send('You\'re not dumb, you\'re learning')


def setup(bot):
    bot.add_cog(AntiSelfDeprecation(bot))
