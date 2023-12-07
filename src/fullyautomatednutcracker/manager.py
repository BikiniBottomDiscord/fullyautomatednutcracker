from utils.async_base_cog_manager import Manager


async def setup(bot):
    await bot.add_cog(Manager(bot, "fullyautomatednutcracker"))
