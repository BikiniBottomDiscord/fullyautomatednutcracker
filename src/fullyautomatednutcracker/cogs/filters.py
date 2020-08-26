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

    @staticmethod
    async def save_gif_and_send(imgs: [Image], channel: discord.TextChannel, file_name="filter.gif", optimize=False, duration=20):
        bytes_fp = io.BytesIO()
        imgs[0].save(bytes_fp, format="GIF", optimize=optimize, save_all=True, append_images=imgs[1:],
                     loop=0, duration=duration, transparency=255, disposal=2)
        bytes_fp.seek(0)
        await channel.send(file=discord.File(bytes_fp, file_name))

    @commands.command(aliases=["gay", "rainbow","mod"])
    async def gaygaygay(self, ctx, inv_object: typing.Union[discord.Member, discord.PartialEmoji]=None):
        if not inv_object or isinstance(inv_object, discord.Member):
            member = inv_object or ctx.author
            downloaded_pfp = image_from_url(member.avatar_url, "image/png")
            resized_pfp = resize(downloaded_pfp, 250)
            gay_filter = Image.open('content/filters/gaygaygay.png')
            resized_filter = resize(gay_filter, 250)
            resized_pfp.paste(resized_filter, (0, 0), resized_filter)
            await self.save_img_and_send(resized_pfp, ctx.channel, file_name="gaygaygay.png")
            downloaded_pfp.close()
            gay_filter.close()
            resized_pfp.close()
            resized_filter.close()
        else:
            downloaded_emoji = image_from_url(inv_object.url, "image/png")

            bands = downloaded_emoji.split()
            width_diff = abs(downloaded_emoji.size[0] - 250)
            height_diff = abs(downloaded_emoji.size[1] - 250)
            if height_diff > width_diff:
                size = (250, downloaded_emoji.size[1] * 250 // downloaded_emoji.size[0])
            else:
                size = (downloaded_emoji.size[0] * 250 // downloaded_emoji.size[1], 250)
            bands = [b.resize(size, Image.LINEAR) for b in bands]
            resized_emoji = Image.merge('RGBA', bands)

            gay_filter = Image.open('content/filters/gaygaygay.png')
            bands = gay_filter.split()
            bands = [b.resize(resized_emoji.size, Image.LINEAR) for b in bands]
            resized_filter = Image.merge('RGBA', bands)

            resized_emoji.paste(resized_filter, (0, 0), resized_filter)
            await self.save_img_and_send(resized_emoji, ctx.channel, file_name="gaygaygay.png")
            downloaded_emoji.close()
            gay_filter.close()
            resized_emoji.close()
            resized_filter.close()

    @commands.command(aliases=["inv"])
    async def invert(self, ctx, inv_object: typing.Union[discord.Member, discord.PartialEmoji]=None):
        if not inv_object or isinstance(inv_object, discord.Member):
            member = inv_object or ctx.author
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

            bands = downloaded_emoji.split()
            width_diff = abs(downloaded_emoji.size[0] - 250)
            height_diff = abs(downloaded_emoji.size[1] - 250)
            if height_diff > width_diff:
                size = (250, downloaded_emoji.size[1] * 250 // downloaded_emoji.size[0])
            else:
                size = (downloaded_emoji.size[0] * 250 // downloaded_emoji.size[1], 250)
            bands = [b.resize(size, Image.LINEAR) for b in bands]
            resized_emoji = Image.merge('RGBA', bands)

            bands = resized_emoji.split()
            bands = [ImageOps.invert(b) for b in bands[:-1]] + [bands[-1]]
            resized_emoji = Image.merge('RGBA', bands)

            await self.save_img_and_send(resized_emoji, ctx.channel, file_name="invert.png")
            downloaded_emoji.close()
            resized_emoji.close()

    @commands.command()
    async def hypify(self, ctx, inv_object: typing.Union[discord.Member, discord.PartialEmoji] = None):
        if not inv_object or isinstance(inv_object, discord.Member):
            member = inv_object or ctx.author
            downloaded_pfp = image_from_url(member.avatar_url, "image/png")
            resized_pfp = resize(downloaded_pfp, 250)
            gay_filter = Image.open('content/filters/20hype_arms.png')
            resized_filter = resize(gay_filter, 230)
            resized_pfp.paste(resized_filter, (0, -10), resized_filter)
            await self.save_img_and_send(resized_pfp, ctx.channel, file_name="20hype_arms.png")
            downloaded_pfp.close()
            gay_filter.close()
            resized_pfp.close()
            resized_filter.close()
        else:
            downloaded_emoji = image_from_url(inv_object.url, "image/png")

            bands = downloaded_emoji.split()
            width_diff = abs(downloaded_emoji.size[0] - 250)
            height_diff = abs(downloaded_emoji.size[1] - 250)
            if height_diff > width_diff:
                size = (250, downloaded_emoji.size[1] * 250 // downloaded_emoji.size[0])
            else:
                size = (downloaded_emoji.size[0] * 250 // downloaded_emoji.size[1], 250)
            bands = [b.resize(size, Image.LINEAR) for b in bands]
            resized_emoji = Image.merge('RGBA', bands)

            hype_arms = Image.open('content/filters/20hype_arms.png')
            bands = hype_arms.split()
            bands = [b.resize(resized_emoji.size, Image.LINEAR) for b in bands]
            resized_filter = Image.merge('RGBA', bands)

            resized_emoji.paste(resized_filter, (0, -10), resized_filter)
            await self.save_img_and_send(resized_emoji, ctx.channel, file_name="20hype_arms.png")
            downloaded_emoji.close()
            hype_arms.close()
            resized_emoji.close()
            resized_filter.close()

    @commands.command()
    async def shake(self, ctx, inv_object: typing.Union[discord.Member, discord.PartialEmoji] = None, zoom_level: float=1.3, shake_strenght: int=5):
        def shake_image(image: Image):
            gif = []
            shake_offsets = [
                (-(int(image.size[0]*zoom_level) - image.size[0]) // 2, -(int(image.size[1]*zoom_level) - image.size[1]) // 2),
                (-(int(image.size[0]*zoom_level) - image.size[0]) // 2 + shake_strenght, -(int(image.size[1]*zoom_level) - image.size[1]) // 2 + shake_strenght),
                (-(int(image.size[0]*zoom_level) - image.size[0]) // 2 + 2 * shake_strenght, -(int(image.size[1]*zoom_level) - image.size[1]) // 2),
            ]

            rbands = image.split()
            rbands = [b.resize((int(image.size[0]*zoom_level), int(image.size[1]*zoom_level)), Image.LINEAR) for b in rbands]
            zoomed_image = Image.merge('RGBA', rbands)

            for idx, offset in enumerate(shake_offsets):
                gif.append(Image.new("RGBA", image.size, (255, 255, 255, 0)))
                gif[-1].paste(zoomed_image, offset, zoomed_image)

                alpha = gif[-1].split()[-1]
                gif[-1] = gif[-1].convert('RGB').convert('P', palette=Image.ADAPTIVE, colors=255)
                mask = Image.eval(alpha, lambda a: 255 if a <= 128 else 0)
                gif[-1].paste(255, mask)

            return gif

        # clamp value
        zoom_level = min(max(0.5, zoom_level), 3.0)
        shake_strenght = min(max(1, shake_strenght), 125)
        if not inv_object or isinstance(inv_object, discord.Member):
            member = inv_object or ctx.author
            downloaded_pfp = image_from_url(member.avatar_url, "image/png")
            resized_pfp = resize(downloaded_pfp, 250)
            shaked_pfp = shake_image(resized_pfp)
            await self.save_gif_and_send(shaked_pfp, ctx.channel, file_name="shake.gif")
            downloaded_pfp.close()
            resized_pfp.close()
        else:
            downloaded_emoji = image_from_url(inv_object.url, "image/png")

            bands = downloaded_emoji.split()
            width_diff = abs(downloaded_emoji.size[0] - 250)
            height_diff = abs(downloaded_emoji.size[1] - 250)
            if height_diff > width_diff:
                size = (250, downloaded_emoji.size[1] * 250 // downloaded_emoji.size[0])
            else:
                size = (downloaded_emoji.size[0] * 250 // downloaded_emoji.size[1], 250)
            bands = [b.resize(size, Image.LINEAR) for b in bands]
            resized_emoji = Image.merge('RGBA', bands)

            shaked_emoji = shake_image(resized_emoji)
            await self.save_gif_and_send(shaked_emoji, ctx.channel, file_name="shake.gif")
            downloaded_emoji.close()
            resized_emoji.close()

    @commands.command(aliases=['rotate', 'spincc', 'scc', 'rcc', 'rotatecc'])
    async def spin(self, ctx, inv_object: typing.Union[discord.Member, discord.PartialEmoji] = None, speed: int=20):
        await self._spin(ctx, inv_object, speed, direction=1)

    @commands.command(aliases=['antirotate', 'spinc', 'sc', 'rc', 'rotatec'])
    async def antispin(self, ctx, inv_object: typing.Union[discord.Member, discord.PartialEmoji] = None, speed: int=20):
        await self._spin(ctx, inv_object, speed, direction=-1)

    async def _spin(self, ctx, inv_object: typing.Union[discord.Member, discord.PartialEmoji] = None, speed: int=20, direction=1):
        def spin_image(image: Image):
            gif = []
            frames = 20
            r_step = 360 / frames
            w = image.size[0]
            h = image.size[1]

            print(w, h)

            rotated_size = (int((image.size[0] ** 2 + image.size[1] ** 2) ** 0.5), int((image.size[0] ** 2 + image.size[1] ** 2) ** 0.5))

            for i in range(frames):
                gif.append(Image.new("RGBA", rotated_size, (255, 255, 255, 0)))
                gif[-1].paste(image, ((rotated_size[0] - w) // 2, (rotated_size[1] - h) // 2), image)
                gif[-1] = gif[-1].rotate(r_step * i * direction)

                alpha = gif[-1].split()[-1]
                gif[-1] = gif[-1].convert('RGB').convert('P', palette=Image.ADAPTIVE, colors=255)
                mask = Image.eval(alpha, lambda a: 255 if a <= 128 else 0)
                gif[-1].paste(255, mask)

            return gif

        # clamp value
        speed = min(max(20, speed), 1000)
        if not inv_object or isinstance(inv_object, discord.Member):
            member = inv_object or ctx.author
            downloaded_pfp = image_from_url(member.avatar_url, "image/png")
            resized_pfp = resize(downloaded_pfp, 250)
            shaked_pfp = spin_image(resized_pfp)
            await self.save_gif_and_send(shaked_pfp, ctx.channel, file_name="spin.gif", duration=speed)
            downloaded_pfp.close()
            resized_pfp.close()
        else:
            downloaded_emoji = image_from_url(inv_object.url, "image/png")

            bands = downloaded_emoji.split()
            width_diff = abs(downloaded_emoji.size[0] - 250)
            height_diff = abs(downloaded_emoji.size[1] - 250)
            if height_diff > width_diff:
                size = (250, downloaded_emoji.size[1] * 250 // downloaded_emoji.size[0])
            else:
                size = (downloaded_emoji.size[0] * 250 // downloaded_emoji.size[1], 250)
            bands = [b.resize(size, Image.LINEAR) for b in bands]
            resized_emoji = Image.merge('RGBA', bands)

            shaked_emoji = spin_image(resized_emoji)
            await self.save_gif_and_send(shaked_emoji, ctx.channel, file_name="spin.gif", duration=speed)
            downloaded_emoji.close()
            resized_emoji.close()


def setup(bot):
    bot.add_cog(Filters(bot))
