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

        answers = ['rock', 'paper', 'scissors']
        await ctx.send('Thinking of my answer ...'
        RESPONSE = random.randint(0, 2)
        await asyncio.sleep(0.8)
        await ctx.send('Got it! Awaiting response.')
        try:
            MESSAGE = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author and message.channel == ctx.channel and message.content in answers, timeout=30.0)
        except asyncio.TimeoutError:
            await ctx.send(f'{ctx.author.mention} took too long to respond, game over')
            return
        await ctx.send(OPTIONS[RESPONSE])
        await asyncio.sleep(0.6)
        if MESSAGE.content.lower() == "rock" and RESPONSE == 2:
            await ctx.send("https://cdn.discordapp.com/attachments/742559349750235136/743267535876653528/you_win.gif")
        elif MESSAGE.content.lower() == "paper" and RESPONSE == 0:
            await ctx.send("https://cdn.discordapp.com/attachments/742559349750235136/743267535876653528/you_win.gif")
        elif MESSAGE.content.lower() == "scissors" and RESPONSE == 1:
            await ctx.send("https://cdn.discordapp.com/attachments/742559349750235136/743267535876653528/you_win.gif")
        elif MESSAGE.content.lower() == "rock" and RESPONSE == 0:
            await ctx.send("https://tenor.com/view/monty-python-draw-gif-5447899")
        elif MESSAGE.content.lower() == "paper" and RESPONSE == 1:
            await ctx.send("https://tenor.com/view/monty-python-draw-gif-5447899")
        elif MESSAGE.content.lower() == "scissors" and RESPONSE == 2:
            await ctx.send("https://tenor.com/view/monty-python-draw-gif-5447899")
        else:
            await ctx.send("https://cdn.discordapp.com/attachments/742559349750235136/743267433615196170/winner.gif")



def setup(bot):
    bot.add_cog(Fun(bot))
