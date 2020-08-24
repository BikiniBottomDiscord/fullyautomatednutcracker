import discord
from discord.ext import commands
import io
import requests
import pillow, Image, ImageDraw
from utils.common_imaging import image_from_url
from utils.common_imaging import resize
class Filters(commands.Cog):
    """Filters!"""
    def __init__(self, bot):
        self.bot = bot

    def resize(self, im, size):
        bands = im.split()
        bands = [b.resize((size, size), Image.LINEAR) for b in bands]
        return Image.merge('RGBA', bands)

    def image_from_url(self, url, content_type):
        try:
            response = requests.get(url)
            img = Image.open(io.BytesIO(response.content))
            if content_type != 'image/gif':
                img = img.convert('RGBA')
            return img
        except Exception as ex:
            return None

    @commands.command()
    async def piltest(self,ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        downloaded_pfp = image_from_url(member.avatar_url, "image/png")
        resized_pfp = resize(downloaded_pfp, 250)
        filter = Image.open('gaygaygay.png')
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



def setup(bot):g
    bot.add_cog(Filters(bot))
    