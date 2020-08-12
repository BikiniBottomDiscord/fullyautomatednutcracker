
import discord

from discord.ext import commands


class Info(commands.Cog):
    """Information commands or something idk"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(rate=1, per=60)
    async def joinpos(self, ctx, member: discord.Member = None):
        """Calculates your join position."""
        member = member if member else ctx.author
        order = sorted((await ctx.guild.fetch_members().flatten()), key=lambda m: m.joined_at)
        join_pos = order.index(member) + 1
        await ctx.send(join_pos)


def setup(bot):
    bot.add_cog(Info(bot))
