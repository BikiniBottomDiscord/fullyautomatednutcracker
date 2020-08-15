import discord
import re
import argparse

from discord.ext import commands


class FetchedUser(commands.Converter):
    async def convert(self, ctx, argument):
        if not argument.isdigit():
            raise commands.BadArgument('Not a valid user ID.')
        try:
            return await ctx.bot.fetch_user(argument)
        except discord.NotFound:
            raise commands.BadArgument('User not found.') from None
        except discord.HTTPException:
            raise commands.BadArgument('An error occurred while fetching the user.') from None


class FetchedChannel(commands.Converter):
    async def convert(self, ctx, argument):
        if not argument.isdigit():
            raise commands.BadArgument('Not a valid channel ID.')
        try:
            return await ctx.bot.fetch_channel(argument)
        except discord.NotFound:
            raise commands.BadArgument('Channel not found.') from None
        except discord.HTTPException:
            raise commands.BadArgument('An error occurred while fetching the channel.') from None


class FetchedGuild(commands.Converter):
    async def convert(self, ctx, argument):
        if not argument.isdigit():
            raise commands.BadArgument('Not a valid guild ID.')
        try:
            return await ctx.bot.fetch_guild(argument)
        except discord.NotFound:
            raise commands.BadArgument('Guild not found.') from None
        except discord.HTTPException:
            raise commands.BadArgument('An error occurred while fetching the guild.') from None


class CachedGuild(commands.Converter):
    async def convert(self, ctx, argument):
        if not argument.isdigit():
            raise commands.BadArgument('Not a valid guild ID.')
        try:
            return ctx.bot.get_guild(argument)
        except discord.NotFound:
            raise commands.BadArgument('Guild not found.') from None
        except discord.HTTPException:
            raise commands.BadArgument('An error occurred while fetching the guild.') from None


class GlobalChannel(commands.Converter):
    async def convert(self, ctx, argument):
        try:
            return await commands.TextChannelConverter().convert(ctx, argument)
        except commands.BadArgument:
            # Not found... so fall back to ID + global lookup
            try:
                channel_id = int(argument, base=10)
            except ValueError:
                raise commands.BadArgument(f'Could not find a channel by ID {argument!r}.')
            else:
                channel = ctx.bot.get_channel(channel_id)
                if channel is None:
                    raise commands.BadArgument(f'Could not find a channel by ID {argument!r}.')
                return channel


class Command(commands.Converter):
    async def convert(self, ctx, argument):
        command = ctx.bot.get_command(argument)
        if command:
            return command
        else:
            raise commands.BadArgument("A command with this name could not be found.")


class Module(commands.Converter):
    async def convert(self, ctx, argument):
        cog = ctx.bot.get_cog(argument)
        if cog:
            return cog
        else:
            raise commands.BadArgument("A module with this name could not be found.")


class OptionFlag(commands.Converter):
    async def convert(self, ctx, argument):
        if not argument.startswith('--'):
            raise commands.BadArgument()
        return argument[2:]


# ===== UNTESTED =====

def argparse_options(*args, parser=None):
    if (not args and not parser) or (args and parser):
        raise Exception("ArgparseOptions could not be created.")

    parser = parser if parser else argparse.ArgumentParser()
    for arg in args:
        parser.add_argument(f"--{arg}")

    class ArgparseOptions(commands.Converter):
        async def convert(self, ctx, argument):
            parsed = parser.parse_args(argument.split())
            return parsed

    return ArgparseOptions


# --([^\s\n]+)\s+(?:\"([^\n]+)\"|([^\s\n-]+))?




