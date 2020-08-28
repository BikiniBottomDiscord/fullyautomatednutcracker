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

    @commands.command()
    async def trans(self, ctx, inv_obj: Optional[Union[discord.Member, discord.PartialEmoji]] = None):
        if not inv_obj or isinstance(inv_obj, discord.Member):
            member = inv_obj or ctx.author
            image = image_from_url(member.avatar_url, 'image/png')
            resized_pfp = resize(image, 250)
            trans_filter = Image.open('content/filters/transflag.png')
            resized_filter = resize(trans_filter, 250)
            resized_pfp.paste(resized_filter, (0, 0), resized_filter)
            await self.save_img_and_send(resized_pfp, ctx.channel, file_name='trans.png')
            image.close()
            resized_pfp.close()
            trans_filter.close()
            resized_filter.close()
        else:
            image = image_from_url(inv_obj.url, "image/png")
            bands = image.split()
            width_diff = abs(image.width - 250)
            height_diff = abs(image.height - 250)
            if width_diff > height_diff:
                size = (250, image.height * 250 // image.width)
            else:
                size = (image.width * 250 // image.height, 250)
            bands = [b.resize(size, Image.LINEAR) for b in bands]
            resized_image = Image.merge('RGBA', bands)
            trans_filter = Image.open('content/filters/transflag.png')
            bands = trans_filter.split()
            bands = [b.resize(resized_image.size, Image.LINEAR) for b in bands]
            resized_trans_filter = Image.merge('RGBA', bands)
            resized_trans_filter.putalpha(185)
            resized_image.paste(resized_trans_filter, (0, 0), resized_trans_filter)

            await self.save_img_and_send(resized_image, ctx.channel, file_name='trans.png')
            image.close()
            resized_image.close()
            trans_filter.close()
            resized_trans_filter.close()

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
    async def rgbsplit(self, ctx, inv_obj: Optional[Union[discord.Member, discord.PartialEmoji]] = None,
                       focus: int = 10):
        def rbgsplit(image: Image, focus: int):
            data = image.getdata()
            blank = (0, 0, 0, 0)
            r = [(d[0], 0, 0, 200) if not d[3] < 10 else blank for d in data]
            g = [(0, d[1], 0, 160) if not d[3] < 10 else blank for d in data]
            b = [(0, 0, d[2], 120) if not d[3] < 10 else blank for d in data]
            a = [(0, 0, 0, (255 - int(sum(d) // len(d)))) if not d[3] < 10 else blank for d in data]
            new_red, new_green, new_blue, alpha, final = Image.new("RGBA", (image.size[0], image.size[1])), \
                                                         Image.new("RGBA", (image.size[0], image.size[1])), Image.new(
                "RGBA", (image.size[0], image.size[1])), \
                                                         Image.new("RGBA", (image.size[0], image.size[1])), Image.new(
                "RGBA", (image.size[0], image.size[1]))

            focus = min(max(focus, 0), 50)

            new_red.putdata(r)
            new_green.putdata(g)
            new_blue.putdata(b)
            alpha.putdata(a)

            final.paste(new_red, (0, 0), new_red)
            final.paste(new_green, (4 * int(focus // 10), 6 * int(focus // 10)), new_green)
            final.paste(new_blue, (8 * int(focus // 10), 12 * int(focus // 10)), new_blue)
            final.paste(alpha, (0, 0), alpha)
            final_image = final.crop((8 * int(focus // 10), 12 * int(focus // 10),
                                      image.size[0] - (4 * int(focus // 10)), image.size[1] - (8 * int(focus // 10))))

            new_red.close()
            new_blue.close()
            new_green.close()

            return final_image

        if not inv_obj or isinstance(inv_obj, discord.Member):
            member = inv_obj or ctx.author
            image = image_from_url(member.avatar_url, "image/png")
            resized_pfp = resize(image, 250)
            final = rbgsplit(resized_pfp, focus)

            await self.save_img_and_send(final, ctx.channel, 'rgbsplit.png')
            image.close()
            resized_pfp.close()
            final.close()
        else:
            downloaded_emoji = image_from_url(inv_obj.url, "image/png")

            bands = downloaded_emoji.split()
            width_diff = abs(downloaded_emoji.size[0] - 250)
            height_diff = abs(downloaded_emoji.size[1] - 250)
            if height_diff > width_diff:
                size = (250, downloaded_emoji.size[1] * 250 // downloaded_emoji.size[0])
            else:
                size = (downloaded_emoji.size[0] * 250 // downloaded_emoji.size[1], 250)
            bands = [b.resize(size, Image.LINEAR) for b in bands]
            resized_emoji = Image.merge('RGBA', bands)
            final = rbgsplit(resized_emoji, focus)
            await self.save_img_and_send(final, ctx.channel, 'rgbsplit.png')
            downloaded_emoji.close()
            resized_emoji.close()
            final.close()

    @commands.command()
    async def shake(self, ctx, inv_object: typing.Union[discord.Member, discord.PartialEmoji] = None, zoom_level: float=1.3, shake_strength: int=5):
        def shake_image(image: Image):
            gif = []
            shake_offsets = [
                (-(int(image.size[0]*zoom_level) - image.size[0]) // 2, -(int(image.size[1]*zoom_level) - image.size[1]) // 2),
                (-(int(image.size[0]*zoom_level) - image.size[0]) // 2 + shake_strength, -(int(image.size[1]*zoom_level) - image.size[1]) // 2 + shake_strength),
                (-(int(image.size[0]*zoom_level) - image.size[0]) // 2 + 2 * shake_strength, -(int(image.size[1]*zoom_level) - image.size[1]) // 2),
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
        shake_strength = min(max(1, shake_strength), 125)
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

    @commands.command()
    async def triggered(self, ctx, inv_object: Union[discord.Member, discord.PartialEmoji] = None,
                        zoom_level: float = 1.3, shake_strength: int = 5):
        def shake_and_trigger_image(image: Image):
            gif = []
            shake_offsets = [
                (-(int(image.size[0] * zoom_level) - image.size[0]) // 2,
                 -(int(image.size[1] * zoom_level) - image.size[1]) // 2),
                (-(int(image.size[0] * zoom_level) - image.size[0]) // 2 + shake_strength,
                 -(int(image.size[1] * zoom_level) - image.size[1]) // 2 + shake_strength),
                (-(int(image.size[0] * zoom_level) - image.size[0]) // 2 + 2 * shake_strength,
                 -(int(image.size[1] * zoom_level) - image.size[1]) // 2),
            ]

            rbands = image.split()
            rbands = [b.resize((int(image.size[0] * zoom_level), int(image.size[1] * zoom_level)), Image.LINEAR) for b
                      in rbands]
            zoomed_image = Image.merge('RGBA', rbands)
            triggered_image = Image.open("content/filters/triggered.png")
            tbands = triggered_image.split()
            tbands = [b.resize((image.width + 20, int(image.height // 4) + 20), Image.LINEAR) for b in tbands]
            triggered_image = Image.merge('RGBA', tbands)

            trigger_offsets = [
                (-((-shake_strength + int(image.size[1] // 5) - 2 * shake_strength) // 2) + shake_strength,
                 (image.size[1] - (int(triggered_image.size[1]) - int(image.size[1] // 5))) - (
                             int(triggered_image.size[1]) // 2 + shake_strength)),
                (-((-shake_strength + int(image.size[1] // 5) - 2) // 2) + shake_strength,
                 (image.size[1] - (int(triggered_image.size[1] - int(image.size[1] // 5)))) - (
                             int(triggered_image.size[1]) // 2)),
                (-((-shake_strength + int(image.size[1] // 5) - 2 * shake_strength) // 2),
                 (image.size[1] - (int(triggered_image.size[1] - int(image.size[1] // 5)))) - int(
                     triggered_image.size[1]) // 2 + 2 * shake_strength),
            ]

            for idx, offset in enumerate(shake_offsets):
                gif.append(Image.new("RGBA", image.size, (255, 255, 255, 0)))
                gif[-1].paste(zoomed_image, offset, zoomed_image)
                gif[-1].paste(triggered_image, (trigger_offsets[idx][0], trigger_offsets[idx][1]), triggered_image)

                alpha = gif[-1].split()[-1]
                gif[-1] = gif[-1].convert('RGB').convert('P', palette=Image.ADAPTIVE, colors=255)
                mask = Image.eval(alpha, lambda a: 255 if a <= 128 else 0)
                gif[-1].paste(255, mask)

            return gif

        # clamp value
        zoom_level = min(max(0.5, zoom_level), 3.0)
        shake_strength = min(max(1, shake_strength), 10)
        if not inv_object or isinstance(inv_object, discord.Member):
            member = inv_object or ctx.author
            downloaded_pfp = image_from_url(member.avatar_url, "image/png")
            resized_pfp = resize(downloaded_pfp, 250)
            shaked_pfp = shake_and_trigger_image(resized_pfp)
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

            shaked_emoji = shake_and_trigger_image(resized_emoji)
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
