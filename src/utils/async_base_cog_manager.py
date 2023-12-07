import os
import sys
import json
import traceback

from discord.ext import commands

from utils.async_base_cog import AsyncBaseCog
from utils import checks


class Manager(AsyncBaseCog, name="Manager"):
    """Generic Async Cog Manager; handles loading, reloading, unloading, enabling, disabling, viewing, and refreshing internal cogs"""

    def __init__(self, bot, namespace):
        super().__init__(bot)

        self.logger.info("loading cog manager settings")
        self.namespace = namespace
        with open(f"config/{self.namespace}_cog_manager.json", "r") as fp:
            self.cog_settings = json.load(fp)

        before = len(self.cog_settings)
        cogs = self.get_all_cogs()

        # Apply cog defaults
        for cog in cogs:
            self.cog_settings[cog] = self.cog_settings.get(cog, True)

        if len(self.cog_settings) != before:
            self.logger.info("saving new defaults")
            self._save_settings()

        self.logger.info(f"{len(cogs)} cogs available, {len([c for c in self.cog_settings if self.cog_settings[c]])} enabled")

    def _save_settings(self):
        with open(f"config/{self.namespace}_cog_manager.json", "w") as fp:
            json.dump(self.cog_settings, fp)

    def get_all_cogs(self):
        """Fetch all available cogs from the cog directory"""
        return [f[:-3] for f in os.listdir(f"{self.namespace}/cogs/") if f.endswith('.py')]

    async def load_all_cogs(self):
        """Load all enabled cogs"""
        loaded = 0
        total = 0
        cogs = self.cog_settings
        for cog in cogs:
            # If the cog is disabled, ignore loading it
            if not self.cog_settings[cog]:
                continue
            # Otherwise, try to load it
            if await self.load_cog(cog):
                loaded += 1
            total += 1
        return loaded, total

    async def load_cog(self, cog_name: str):
        """Attempt to load a cog by its filename"""
        try:
            self.logger.info(f"attempting to load cog {cog_name}")
            await self.bot.load_extension(f"{self.namespace}.cogs.{cog_name}")
        except Exception as ex:
            self.logger.info("could not initialize")
            self.logger.info(''.join(traceback.format_exception(type(ex), ex, ex.__traceback__)))
            return False
        try:
            self.logger.info(f"loaded, finding on load")
            for loaded_cog_name, loaded_cog_class in self.bot.cogs.items():
                if cog_name == os.path.basename(sys.modules[loaded_cog_class.__class__.__module__].__file__).replace(".py", ""):
                    self.logger.info(f"found on load")
                    await self.bot.get_cog(loaded_cog_name).on_cog_loaded()
                    return True
            self.logger.info(f"could not find on load, removing extension")
            await self.bot.unload_extension(f"{self.namespace}.cogs.{cog_name}")
            return False
        except Exception as ex:
            self.logger.info("error in on load, removing extension")
            self.logger.info(''.join(traceback.format_exception(type(ex), ex, ex.__traceback__)))
            try:
                await self.bot.unload_extension(f"{self.namespace}.cogs.{cog_name}")
            except Exception as ex:
                self.logger.info("bigger oof, couldn't unload now")
                self.logger.info(''.join(traceback.format_exception(type(ex), ex, ex.__traceback__)))
            return False

    async def unload_all_cogs(self):
        """Unload all enabled cogs"""
        unloaded = 0
        total = 0
        cogs = self.cog_settings
        for cog in cogs:
            # If the cog is disabled, ignore unloading it
            if not self.cog_settings[cog]:
                continue
            # Otherwise, try to unload it
            if await self.unload_cog(cog):
                unloaded += 1
            total += 1
        return unloaded, total

    async def unload_cog(self, cog_name):
        """Attempt to load a cog by its filename"""
        try:
            self.logger.info(f"attempting to find on unload")
            for loaded_cog_name, loaded_cog_class in self.bot.cogs.items():
                if cog_name == os.path.basename(sys.modules[loaded_cog_class.__class__.__module__].__file__).replace(".py", ""):
                    self.logger.info(f"found on unload")
                    await self.bot.get_cog(loaded_cog_name).on_cog_unload()
                    await self.bot.unload_extension(f"{self.namespace}.cogs.{cog_name}")
                    return True
            self.logger.info(f"could not find on unload, removing extension")
            await self.bot.unload_extension(f"{self.namespace}.cogs.{cog_name}")
            return False
        except Exception as ex:
            self.logger.info("error in on unload, removing extension")
            self.logger.info(''.join(traceback.format_exception(type(ex), ex, ex.__traceback__)))
            try:
                await self.bot.unload_extension(f"{self.namespace}.cogs.{cog_name}")
            except Exception as ex:
                self.logger.info("bigger oof, couldn't unload now")
                self.logger.info(''.join(traceback.format_exception(type(ex), ex, ex.__traceback__)))
            return False

    async def reload_cog(self, cog_name):
        """Attempt to reload a cog by its filename"""

        self.logger.info(f"attempting to unload")
        _ = await self.unload_cog(cog_name)

        self.logger.info(f"attempting to load")
        success = await self.load_cog(cog_name)
        return success

    @commands.group(invoke_without_command=True)
    @checks.is_admin()
    async def cog(self, ctx):
        """Cog action group"""
        await ctx.send_help(self.cog)

    @cog.command(aliases=[])
    async def load(self, ctx, cog_name):
        """Load an unloaded active cog given a cog filename"""
        self.logger.info(f"{ctx.author.id} `cog load` invoked by '{ctx.author.name}' [{cog_name}]")
        if cog_name not in self.cog_settings:
            await ctx.message.reply(f"Could not find cog `{cog_name}`.", mention_author=False)
        elif not self.cog_settings[cog_name]:
            await ctx.message.reply(f"Cog `{cog_name}` is disabled.", mention_author=False)
        elif await self.load_cog(cog_name):
            await ctx.message.reply(f"`{cog_name}` loaded.", mention_author=False)
        else:
            await ctx.message.reply(f"`{cog_name}` was not loaded. Check logs.", mention_author=False)

    @cog.command(aliases=[])
    async def unload(self, ctx, cog_name):
        """Unload a loaded cog given a cog filename"""
        self.logger.info(f"{ctx.author.id} `cog unload` invoked by '{ctx.author.name}' [{cog_name}]")
        if cog_name not in self.cog_settings:
            await ctx.message.reply(f"Could not find cog `{cog_name}`.", mention_author=False)
        elif await self.unload_cog(cog_name):
            await ctx.message.reply(f"`{cog_name}` unloaded.", mention_author=False)
        else:
            await ctx.message.reply(f"`{cog_name}` was not unloaded. Check logs.", mention_author=False)

    @cog.command(aliases=[])
    async def reload(self, ctx, cog_name):
        """Reload a loaded active cog given a cog filename"""
        self.logger.info(f"{ctx.author.id} `cog reload` invoked by '{ctx.author.name}' [{cog_name}]")
        if cog_name not in self.cog_settings:
            await ctx.message.reply(f"Could not find cog `{cog_name}`.", mention_author=False)
        elif not self.cog_settings[cog_name]:
            await ctx.message.reply(f"Cog `{cog_name}` is disabled.", mention_author=False)
        elif await self.reload_cog(cog_name):
            await ctx.message.reply(f"`{cog_name}` reloaded.", mention_author=False)
        else:
            await ctx.message.reply(f"`{cog_name}` was not reloaded. Check logs.", mention_author=False)

    @cog.command(aliases=[])
    async def enable(self, ctx, cog_name):
        """Enable a disabled cog given a cog filename and load it"""
        self.logger.info(f"{ctx.author.id} `cog enable` invoked by '{ctx.author.name}' [{cog_name}]")
        if cog_name not in self.cog_settings:
            await ctx.message.reply(f"Could not find cog `{cog_name}`.", mention_author=False)
        elif self.cog_settings[cog_name]:
            await ctx.message.reply(f"Cog `{cog_name}` is already enabled.", mention_author=False)
        else:
            self.cog_settings[cog_name] = True
            self._save_settings()
            if await self.load_cog(cog_name):
                await ctx.message.reply(f"`{cog_name}` enabled and loaded.", mention_author=False)
            else:
                await ctx.message.reply(f"`{cog_name}` enabled but was not loaded. Check logs.", mention_author=False)

    @cog.command(aliases=[])
    async def disable(self, ctx, cog_name):
        """Disable an active cog given a cog filename and attempt to unload it"""
        self.logger.info(f"{ctx.author.id} `cog disable` invoked by '{ctx.author.name}' [{cog_name}]")
        if cog_name not in self.cog_settings:
            await ctx.message.reply(f"Could not find cog `{cog_name}`.", mention_author=False)
        elif not self.cog_settings[cog_name]:
            await ctx.message.reply(f"Cog `{cog_name}` is already disabled.", mention_author=False)
        else:
            self.cog_settings[cog_name] = False
            self._save_settings()
            if await self.unload_cog(cog_name):
                await ctx.message.reply(f"`{cog_name}` disabled and unloaded.", mention_author=False)
            else:
                await ctx.message.reply(f"`{cog_name}` disabled but was not unloaded. Check logs.", mention_author=False)

    @cog.command(aliases=['aload'])
    async def loadall(self, ctx):
        """Load all active cogs available"""
        self.logger.info(f"{ctx.author.id} `cog loadall` invoked by '{ctx.author.name}'")
        loaded, total = await self.load_all_cogs()
        await ctx.message.reply(f"`{loaded} of {total}` successfully loaded", mention_author=False)

    @cog.command(aliases=['aunload'])
    async def unloadall(self, ctx):
        """Unload all active cogs available"""
        self.logger.info(f"{ctx.author.id} `cog unloadall` invoked by '{ctx.author.name}'")
        unloaded, total = await self.unload_all_cogs()
        await ctx.message.reply(f"`{unloaded} of {total}` successfully unloaded", mention_author=False)

    @cog.command(aliases=[])
    async def list(self, ctx):
        """List the cogs available regardless of their loadability status"""
        self.logger.info(f"{ctx.author.id} `cog list` invoked by '{ctx.author.name}'")
        await ctx.message.reply(f"```python\ncog_settings = {json.dumps(self.cog_settings, indent=2)}\n```", mention_author=False)

    @cog.command(aliases=['reloadself'])
    async def refresh(self, ctx):
        """Refresh the manager; unload all cogs, pull the cog settings file, and load all available cogs"""
        self.logger.info(f"{ctx.author.id} `cog refresh` invoked by '{ctx.author.name}'")

        self.logger.info("unloading all cogs")
        unloaded, unload_total = await self.unload_all_cogs()

        self.logger.info("loading cog manager settings")
        with open(f"config/{self.namespace}_cog_manager.json", "r") as fp:
            self.cog_settings = json.load(fp)

        before = len(self.cog_settings)
        cogs = self.get_all_cogs()

        # Apply cog defaults
        for cog in cogs:
            self.cog_settings[cog] = self.cog_settings.get(cog, True)

        if len(self.cog_settings) != before:
            self.logger.info("saving new defaults")
            self._save_settings()

        self.logger.info("loading all cogs")
        loaded, load_total = await self.load_all_cogs()

        await ctx.message.reply(f"`{unloaded} of {unload_total}` successfully unloaded\n`{loaded} of {load_total}` successfully loaded\n\n```python\ncog_settings = {json.dumps(self.cog_settings, indent=2)}\n```", mention_author=False)
