#put all the fun commands here
#IMPORTS
import discord, apraw

from discord.ext import commands
from utils.common import load_reddit_creds
import asyncio
import random

#VARIABLES
OPTIONS = ['Rock!', 'Paper!', 'Scissors!']


class Fun(commands.Cog):
    """Fun commands like quick bot responses or simple games. ex: rock paper scissors"""
    def __init__(self, bot):
        self.bot = bot
        username, password, client_secret, client_id = load_reddit_creds()
        self.bot.reddit = apraw.Reddit(username=username, password=password, client_secret=client_secret, client_id=client_id)

    @commands.command(aliases=["rps"])
    async def rockpaperscissors(self, ctx):
        """A nice game of Rock Paper Scissors. - Alias: rps"""

        answers = ['rock', 'paper', 'scissors']
        await ctx.send('Thinking of my answer ...')
        RESPONSE = random.randint(0, 2)
        await asyncio.sleep(0.8)
        await ctx.send('Got it! Awaiting response.')
        try:
            MESSAGE = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author and message.channel == ctx.channel and message.content.lower() in answers, timeout=30.0)
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
            await ctx.send("https://cdn.discordapp.com/attachments/742559349750235136/744616057763004838/draw.gif")
        elif MESSAGE.content.lower() == "paper" and RESPONSE == 1:
            await ctx.send("https://cdn.discordapp.com/attachments/742559349750235136/744616057763004838/draw.gif")
        elif MESSAGE.content.lower() == "scissors" and RESPONSE == 2:
            await ctx.send("https://cdn.discordapp.com/attachments/742559349750235136/744616057763004838/draw.gif")
        else:
            await ctx.send("https://cdn.discordapp.com/attachments/742559349750235136/743267433615196170/winner.gif")

    @commands.command(aliases=['coot', 'cute'])
    async def aww(self, ctx):
        subreddit = await reddit.subreddit('aww')
        submissions = []
        async for submission in subreddit.hot(limit=50):
            if submission.pinned is False:
                submissions.append(submission)
        post = random.choice(submissions)
        author = await post.author()
        url = 'https://reddit.com' + post.permalink
        embed = custom_embed.CustomEmbed(ctx, color=ctx.author.color)
        embed.title = f"{post.title} - /u/{author} on r/{subreddit.display_name}"
        embed.description = post.selftext or ''
        embed.url = url
        embed.set_image(url=post.url)
        embed.set_footer(text='*if image isn\'t working then it probably is a video*')
        await ctx.send(embed=embed)



def setup(bot):
    bot.add_cog(Fun(bot))
