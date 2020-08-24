import discord
import io

from discord.ext import commands
from PIL import Image

from utils.common_imaging import image_from_url, resize

class Filters(commands.Cog):
    """Filters!"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["gay","rainbow"])
    async def gaygaygay(self, ctx, member: discord.Member =None):
        member = ctx.author if not member else member
        downloaded_pfp = image_from_url(member.avatar_url, "image/png")
        resized_pfp = resize(downloaded_pfp, 250)
        filter = Image.open('content/filters/gaygaygay.png')
        resized_filter = resize(filter, 250)
        resized_pfp.paste(resized_filter, (0, 0), resized_filter)
        bytes_fp = io.BytesIO()
        resized_pfp.save(bytes_fp, quality=95, format="PNG")
        bytes_fp.seek(0)
        downloaded_pfp.close()
        filter.close()
        resized_pfp.close()
        resized_filter.close()
        await ctx.channel.send(file=discord.File(bytes_fp, f"pfp_filter.png"))


def setup(bot):
    bot.add_cog(Filters(bot))
    