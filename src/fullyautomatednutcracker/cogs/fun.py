#put all the fun commands here
#IMPORTS
import discord

from discord.ext import commands

import asyncio
import random

#VARIABLES
OPTIONS = ['Rock!', 'Paper!', 'Scissors!']


class Fun(commands.Cog):
    """Fun commands like quick bot responses or simple games. ex: rock paper scissors"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["rps"])
    async def rockpaperscissors(self, ctx):
        """A nice game of Rock Paper Scissors. - Alias: rps"""
        VERIFY = False
        member = ctx.author
        await ctx.send('Thinking of my answer ...')
        await asyncio.sleep(0.8)
        await ctx.send('Got it! Awaiting response.')
        try:
            while True:
                MESSAGE = await self.bot.wait_for('message', check=(lambda message: message.author == ctx.author), timeout=30)
                if MESSAGE.content == "rock" or MESSAGE.content == "Rock" or MESSAGE.content == "paper" or MESSAGE.content == "Paper" or MESSAGE.content == "scissors" or MESSAGE.content == "Scissors":
                    break
                else:
                    await ctx.send("That's not an answer you frick. Put in either rock, paper or scissors.")
                    MESSAGE = " "
        except asyncio.TimeoutError:
            await ctx.send(f"{ctx.author.mention} timed out!")
            return
        RESPONSE = random.randint(0, 2)
        await ctx.send(OPTIONS[RESPONSE])
        await asyncio.sleep(0.6)
        if MESSAGE.content == "rock" and RESPONSE == 2 or MESSAGE.content == "Rock" and RESPONSE == 2:
            await ctx.send("https://tenor.com/view/the-goon-win-you-won-willy-wonka-oompa-loompa-fc-gif-14046847")
        elif MESSAGE.content == "paper" and RESPONSE == 0 or MESSAGE.content == "Paper" and RESPONSE == 0:
            await ctx.send("https://tenor.com/view/the-goon-win-you-won-willy-wonka-oompa-loompa-fc-gif-14046847")
        elif MESSAGE.content == "scissors" and RESPONSE == 1 or MESSAGE.content == "Scissors" and RESPONSE == 1:
            await ctx.send("https://tenor.com/view/the-goon-win-you-won-willy-wonka-oompa-loompa-fc-gif-14046847")
        elif MESSAGE.content == "rock" and RESPONSE == 0 or MESSAGE.content == "Rock" and RESPONSE == 0:
            await ctx.send("https://tenor.com/view/monty-python-draw-gif-5447899")
        elif MESSAGE.content == "paper" and RESPONSE == 1 or MESSAGE.content == "Paper" and RESPONSE == 1:
            await ctx.send("https://tenor.com/view/monty-python-draw-gif-5447899")
        elif MESSAGE.content == "scissors" and RESPONSE == 2 or MESSAGE.content == "Scissors" and RESPONSE == 2:
            await ctx.send("https://tenor.com/view/monty-python-draw-gif-5447899")


def setup(bot):
    bot.add_cog(Fun(bot))
