import discord

from discord.ext import commands

from utils.async_base_cog_manager import AsyncBaseCog


class Info(AsyncBaseCog):
    """Information commands or something idk"""

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
        embed.set_author(name=str(member), icon_url=member.avatar.url)
        embed.set_image(url=member.avatar.url)
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Info(bot))
