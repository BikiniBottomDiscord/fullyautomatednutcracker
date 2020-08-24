import discord
import io
import typing

from discord.ext import commands
from PIL import Image, ImageOps

from utils.common_imaging import image_from_url, resize


class Filters(commands.Cog):
    """Filters!"""
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    async def save_img_and_send(img: Image, channel: discord.TextChannel, file_name="filter.png", quality=100):
        bytes_fp = io.BytesIO()
        img.save(bytes_fp, format="PNG", quality=quality)
        bytes_fp.seek(0)
        await channel.send(file=discord.File(bytes_fp, file_name))

    @commands.command(aliases=["gay", "rainbow"])
    async def gaygaygay(self, ctx, member: discord.Member =None):
        member = ctx.author if not member else member
        downloaded_pfp = image_from_url(member.avatar_url, "image/png")
        resized_pfp = resize(downloaded_pfp, 250)
        filter = Image.open('content/filters/gaygaygay.png')
        resized_filter = resize(filter, 250)
        resized_pfp.paste(resized_filter, (0, 0), resized_filter)
        await self.save_img_and_send(resized_pfp, ctx.channel, file_name="gaygaygay.png")
        downloaded_pfp.close()
        filter.close()
        resized_pfp.close()
        resized_filter.close()

    @commands.command(aliases=["inv"])
    async def invert(self, ctx, inv_object: typing.Union[discord.Member, discord.Emoji]=None):
        if not inv_object or isinstance(inv_object, discord.Member):
            member = ctx.author if not inv_object else inv_object
            downloaded_pfp = image_from_url(member.avatar_url, "image/png")
            resized_pfp = resize(downloaded_pfp, 250)

            bands = resized_pfp.split()
            bands = [ImageOps.invert(b) for b in bands[:-1]] + [bands[-1]]
            resized_pfp = Image.merge('RGBA', bands)

            await self.save_img_and_send(resized_pfp, ctx.channel, file_name="invert.png")
            downloaded_pfp.close()
            resized_pfp.close()
        else:
            downloaded_emoji = image_from_url(inv_object.url, "image/png")
            resized_emoji = resize(downloaded_emoji, 250)

            bands = resized_emoji.split()
            bands = [ImageOps.invert(b) for b in bands[:-1]] + [bands[-1]]
            resized_emoji = Image.merge('RGBA', bands)

            await self.save_img_and_send(resized_emoji, ctx.channel, file_name="invert.png")
            downloaded_emoji.close()
            resized_emoji.close()


def setup(bot):
    bot.add_cog(Filters(bot))
