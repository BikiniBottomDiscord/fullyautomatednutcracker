
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


def setup(bot):
    bot.add_cog(Info(bot))
