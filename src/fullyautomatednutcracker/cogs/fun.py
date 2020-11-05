# put all the fun commands here
# IMPORTS
import discord
import apraw

from discord.ext import commands
from utils.common import load_reddit_creds
from utils import checks
import asyncio
import random
import math

# VARIABLES
OPTIONS = ['Rock!', 'Paper!', 'Scissors!']


class Fun(commands.Cog):
    """Fun commands like quick bot responses or simple games. ex: rock paper scissors"""
    def __init__(self, bot):
        self.bot = bot
        username, password, client_secret, client_id = load_reddit_creds()
        self.bot.reddit = apraw.Reddit(username=username, password=password, client_secret=client_secret, client_id=client_id)
        self.aww_submissions = []
        self.bot.good = [224323277370294275, 448250281097035777, 562642634686988289, 368880176970596352]

    async def get_submission(self, subreddit):
        if len(self.aww_submissions) == 0:
            async for submission in subreddit.hot(limit=25):
                if submission.pinned is False:
                    self.aww_submissions.append(submission)
        return random.choice(self.aww_submissions)

    @commands.command(aliases=["rps"])
    async def rockpaperscissors(self, ctx):
        """A nice game of Rock Paper Scissors. - Alias: rps"""

        options = ['Rock!', 'Paper!', 'Scissors!']
        answers = {'rock': 0, 'paper': 1, 'scissors': 2}
        await ctx.send('Thinking of my answer ...')
        response = random.randint(0, 2)
        await asyncio.sleep(0.8)
        await ctx.send('Got it! Awaiting response.')
        try:
            MESSAGE = await self.bot.wait_for('message', check=lambda
                message: message.author == ctx.author and message.channel == ctx.channel
                         and message.content.lower() in answers, timeout=30.0)
        except asyncio.TimeoutError:
            await ctx.send(f'{ctx.author.mention} took too long to respond, game over')
            return
        await ctx.send(options[response])
        await asyncio.sleep(0.6)
        result = response - answers[MESSAGE.content.lower()]
        gif = ["https://cdn.discordapp.com/attachments/742559349750235136/744616057763004838/draw.gif",
               "https://cdn.discordapp.com/attachments/742559349750235136/743267433615196170/winner.gif",
               "https://cdn.discordapp.com/attachments/742559349750235136/743267535876653528/you_win.gif"]
        await ctx.send(gif[result])

    @commands.command(aliases=['coot', 'cute'])
    async def aww(self, ctx):
        subreddit = await self.bot.reddit.subreddit('aww')
        post = await self.get_submission(subreddit)
        self.aww_submissions.remove(post)
        author = await post.author()
        url = 'https://reddit.com' + post.permalink
        embed = discord.Embed(color=ctx.author.color)
        embed.title = f"{post.title} - /u/{author} on r/{subreddit.display_name}"
        embed.description = post.selftext or ''
        embed.url = url
        embed.set_image(url=post.url)
        embed.set_footer(text='*if image isn\'t working then it probably is a video*')
        await ctx.send(embed=embed)

    @commands.command(aliases=['mc'])
    async def membercount(self,ctx):
        await ctx.send(f'The Current Member Count Is: {len(ctx.guild.members)}')

    @commands.command(aliases=['gi'])
    async def guildinfo(self,ctx):
        bots = len([x for x in ctx.guild.members if x.bot])
        amtuser = len([x for x in ctx.guild.members if not x.bot])
        embed = discord.Embed(title=(f'{ctx.guild.name}\'s info'), colour=discord.Color(0x67fafb),timestamp=ctx.message.created_at)
        embed.set_footer(text=f"requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.add_field(name='Guild id:', value=ctx.guild.id)
        embed.add_field(name="Members:", value=(f"{amtuser}"))
        embed.add_field(name="Bots:", value=(f'{bots}'))
        embed.add_field(name='Owner:', value=(ctx.guild.owner))
        embed.add_field(name='Roles:', value=(f'{(len(ctx.guild.roles))}'))
        embed.add_field(name="Guild created at:", value=(f'{ctx.guild.created_at.strftime("%Y/%M/%d")}'))
        embed.add_field(name='Total Channels:', value=(f'{len(ctx.guild.channels)}'))
        embed.add_field(name='Total text channels:', value=(f'{len(ctx.guild.text_channels)}'))
        embed.add_field(name='Total voice channels:', value=(f'{len(ctx.guild.voice_channels)}'))
        embed.add_field(name='Total number of emojis', value=(f'{len(ctx.guild.emojis)}'))
        embed.add_field(name='Boost level:', value=(f'{ctx.guild.premium_tier}'))
        await ctx.send(embed=embed)

    @commands.command()
    async def howbad(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        if member.id == 304695409031512064:
            embed = discord.Embed(title=(f'{member}\'s badness level'), colour=member.color)
            embed.add_field(name="They are:", value=(f'100% Bad(dmb)'))
            await ctx.send(embed=embed)
        elif member.id in self.bot.good:
            embed = discord.Embed(title=(f'{member}\'s Good level'), colour=member.color)
            embed.add_field(name="They are:", value=(f'100% Good'))
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title=(f'{ctx.author}\'s badness level'), colour=member.color)
            embed.add_field(name="They are:", value=(f'{random.randint(1, 75)}% Bad'))
            await ctx.send(embed=embed)
    @commands.command():
    async def modcheck(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        modlevel = int(str(member.id)[-2:])

        embed = discord.Embed(title=(f'{member}\'s mod level'), colour=0xff0000 if modlevel > 50 else 0x00ff00)
        embed.add_field(name="They are:", value=(f'{modlevel}% mod {":flushed:" if modlevel == 69 else ":rainbow_flag:" if modlevel > 50 else ""}'))
        await ctx.send(embed=embed)

    @commands.command()
    @checks.is_admin()
    async def add_good(self,ctx, member:discord.Member):
        self.bot.good.append(member.id)
        await ctx.send('Added To Good Person List')


def setup(bot):
    bot.add_cog(Fun(bot))
