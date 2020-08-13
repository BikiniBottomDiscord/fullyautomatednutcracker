
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


def setup(bot):
    bot.add_cog(Info(bot))
