import discord
import io

from discord.ext import commands
from discord import Member, TextChannel
from typing import Union


from utils import checks
from utils.common import is_admin



class Admin(commands.Cog):
    """Admin commands for bot maintenance."""
    def __init__(self, bot):
        self.bot = bot

    def cog_check(self, ctx):
        return is_admin(ctx.author)

    @commands.command(aliases=['kill', 'die'])
    async def close(self, ctx):
        await ctx.send("No u.")
        await self.bot.close()

    @commands.command()
    async def load(self, ctx, cog_name):
        try:
            self.bot.load_extension(f"fullyautomatednutcracker.cogs.{cog_name}")
            await ctx.send(f"Loaded {cog_name}.")
        except Exception as e:
            await ctx.send(f"{e.__class__.__name__}: {e}")

    @commands.command()
    async def unload(self, ctx, cog_name):
        try:
            self.bot.unload_extension(f"fullyautomatednutcracker.cogs.{cog_name}")
            await ctx.send(f"Unloaded {cog_name}.")
        except Exception as e:
            await ctx.send(f"{e.__class__.__name__}: {e}")

    @commands.command()
    async def reload(self, ctx, cog_name):
        try:
            self.bot.reload_extension(f"fullyautomatednutcracker.cogs.{cog_name}")
            await ctx.send(f"Reloaded {cog_name}.")
        except Exception as e:
            await ctx.send(f"{e.__class__.__name__}: {e}")

    @commands.command()
    async def send(self, ctx, destination: Union[TextChannel, Member], *, msg):
        """Send a message + attachments to a channel or member"""
        files = []
        for attachment in ctx.message.attachments:
            file = await attachment.read()
            file = discord.File(io.BytesIO(file))
            files.append(file)
        try:
            await destination.send(content=msg, files=files)
            await ctx.send(f"Sent to {destination}.")
        except discord.Forbidden:
            await ctx.send(f"Could not send to {destination}.")


def setup(bot):
    bot.add_cog(Admin(bot))
