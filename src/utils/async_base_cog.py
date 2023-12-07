import logging

from discord.ext import commands


class AsyncBaseCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info(f"Cog {self.__class__.__name__} initializing")

    async def on_cog_loaded(self):
        """@final No override"""
        self.logger.info(f"Cog {self.__class__.__name__} loading")
        await self._on_cog_loaded()
        self.logger.info(f"Cog {self.__class__.__name__} loaded")

    async def on_cog_unload(self):
        """@final No override"""
        self.logger.info(f"Cog {self.__class__.__name__} unloading")
        await self._on_cog_unload()
        self.logger.info(f"Cog {self.__class__.__name__} unloaded")

    async def _on_cog_loaded(self):
        """Async callback after the cog is initialized"""
        pass

    async def _on_cog_unload(self):
        """Async callback before the cog is about to be unloaded"""
        pass
