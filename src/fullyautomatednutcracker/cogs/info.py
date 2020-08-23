
import discord

from discord.ext import commands


class Info(commands.Cog):
    """Information commands or something idk"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def joinpos(self, ctx, member: discord.Member = None):
        """Calculates your join position."""
        member = member if member else ctx.author
        order = sorted(ctx.guild.members, key=lambda m: m.joined_at)
        join_pos = order.index(member) + 1
        await ctx.send(join_pos)

    @commands.command(aliases=['av', 'pfp'])
    async def avatar(self, ctx, member: discord.Member = None):
        member = member if member else ctx.author
        embed = discord.Embed(title='Avatar', color=member.color)
        embed.set_author(name=str(member), icon_url=member.avatar_url)
        embed.set_image(url=member.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(aliases='mc')
    async def membercount(self,ctx):
        await ctx.send(f'The Current Member Count Is: {len(ctx.guild.members)}')

    @commands.command(aliases='gi')
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


def setup(bot):
    bot.add_cog(Info(bot))
