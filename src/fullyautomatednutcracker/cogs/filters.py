import discord
import io
import re
import typing
import datetime
import requests

from discord.ext import commands
from PIL import Image, ImageOps, ImageDraw, ImageFont

from utils import common_imaging
from utils.common import has_blacklisted_word


class DownloadedAsset:
    def __init__(self, image: Image, supposed_gif: bool):
        self.image = image
        self.is_gif = supposed_gif
        self.size = image.size
        self.height = image.height
        self.width = image.width

        if not supposed_gif:
            self.frames = [self.image]
        else:
            self.frames = []
            try:
                while True:
                    image.seek(image.tell()+1)
                    # do something to im
                    self.frames.append(image.convert('RGBA'))
            except EOFError:
                pass  # end of sequence


class Filters(commands.Cog):
    """Filters!"""
    def __init__(self, bot):
        self.bot = bot
        self.user_image_cache = dict()
        self.url_regex = re.compile(
            r'^(?:http|ftp)s?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        self.__wrapped_conversion = None

    async def wrapped_converter(self, converter, ctx, argument):
        try:
            self.__wrapped_conversion = await converter().convert(ctx, argument)
            return self.__wrapped_conversion
        except:
            return None

    async def get_asset_from_user(self, ctx, allow_images=True, allow_gifs=False) -> typing.Union[DownloadedAsset, None]:
        content = ''.join(ctx.message.content.split(' ')[1:])
        # Fetch a url
        if content == 'me':
            image_url = ctx.author.avatar_url
        elif len(ctx.message.attachments) > 0:
            image_url = ctx.channel.attachments[0]
        elif re.match(self.url_regex, content):
            image_url = content
        # RED ALERT :: RED ALERT :: WRETCHED CODE BELOW :: UPDATE WHEN PY3.8 IS INSTALLED :: RED ALERT :: RED ALERT
        elif await self.wrapped_converter(commands.PartialEmojiConverter, ctx, content):
            image_url = self.__wrapped_conversion.url
        elif await self.wrapped_converter(commands.MemberConverter, ctx, content):
            image_url = self.__wrapped_conversion.avatar_url
        elif await self.wrapped_converter(commands.UserConverter, ctx, content):
            image_url = self.__wrapped_conversion.avatar_url
        elif ctx.author.id in self.user_image_cache and (datetime.datetime.now().timestamp() - self.user_image_cache[ctx.author.id][1]) <= 60 * 15:
            image_url = self.user_image_cache[ctx.author.id][0]
        else:
            await ctx.channel.send("**Error**: I could not find an image in your message or in your 15 minute history.")
            return None
        # Sanitize and check it
        headers = requests.head(image_url).headers
        if "Content-Type" not in headers or ("image/png" not in headers["Content-Type"] and "image/jpeg" not in headers["Content-Type"] and "image/gif" not in headers["Content-Type"]):
            await ctx.channel.send("**Error**: That url does not appear to point to a '.png', '.jpeg/.jpg' or '.gif'. These are the only supported image manipulation types.")
            return None
        if "Content-Length" not in headers or not headers["Content-Length"].isnumeric():
            await ctx.channel.send("**Error**: I cannot manipulate this image as the file size is unknown.")
            return None
        # TODO uncomment if this starts to get out of hand...
        # if (headers["Content-Type"] == "image/png" or headers["Content-Type"] == "image/jpeg") and int(headers["Content-Length"]) > 512000:
        #     await ctx.channel.send("**Error**: The image is too big! It must be less than 512 KB.")
        #     return None
        # if headers["Content-Type"] == "image/gif" and int(headers["Content-Length"]) > 1500000:
        #     await ctx.channel.send("**Error**: The gif is too big! It must be less than 1.5 MB.")
        #     return None
        try:
            if not allow_gifs and headers["Content-Type"] == "image/gif":
                ctype = "image/png"
            elif not allow_images and (headers["Content-Type"] == "image/png" or headers["Content-Type"] == "image/jpeg"):
                ctype = "image/gif"
            else:
                ctype = headers["Content-Type"]
            download = common_imaging.image_from_url(image_url, ctype)
            self.user_image_cache[ctx.author.id] = [image_url, datetime.datetime.now().timestamp()]
            return DownloadedAsset(download, ctype == "image/gif")
        except:
            await ctx.channel.send("**Error**: I could not download or convert that file!")
            return None

    async def save_img_and_send(self, for_user: discord.User, img: Image, channel: discord.TextChannel, file_name="filter.png", quality=100, things_to_close: tuple=()):
        bytes_fp = io.BytesIO()
        img.save(bytes_fp, format="PNG", quality=quality)
        bytes_fp.seek(0)
        message = await channel.send(file=discord.File(bytes_fp, file_name))
        self.user_image_cache[for_user.id] = [message.attachments[0].url, datetime.datetime.now().timestamp()]
        for ttc in things_to_close:
            ttc.close()

    async def save_gif_and_send(self, for_user: discord.User, imgs: [Image], channel: discord.TextChannel, file_name="filter.gif", optimize=False, duration=20, things_to_close: tuple=()):
        bytes_fp = io.BytesIO()
        imgs[0].save(bytes_fp, format="GIF", optimize=optimize, save_all=True, append_images=imgs[1:],
                     loop=0, duration=duration, transparency=255, disposal=2)
        bytes_fp.seek(0)
        message = await channel.send(file=discord.File(bytes_fp, file_name))
        self.user_image_cache[for_user.id] = [message.attachments[0].url, datetime.datetime.now().timestamp()]
        for ttc in things_to_close:
            ttc.close()

    @commands.command()
    async def image(self, ctx):
        download = await self.get_asset_from_user(ctx, allow_gifs=True)
        if not download:
            return
        for idx, frame in enumerate(download.frames):
            # Take the image and resize it with locked aspect ratio to the nearest 250x250
            download.frames[idx] = common_imaging.resize_to_nearest(frame)

        # Ship it
        if download.is_gif:
            await self.save_gif_and_send(ctx.author, download.frames, ctx.channel, file_name="image.gif")
        else:
            await self.save_img_and_send(ctx.author, download.frames[0], ctx.channel, file_name="iamge.png")
        del download

    @commands.command(aliases=["gay", "rainbow", "mod"])
    async def gaygaygay(self, ctx):
        download = await self.get_asset_from_user(ctx)
        if not download:
            return

        # Take the image and resize it with locked aspect ratio to the nearest 250x250
        resized_image = common_imaging.resize_to_nearest(download.image)

        # Open the filter
        gay_filter = Image.open('content/filters/gaygaygay.png')

        # Take the filter and resize it with unlocked aspect ratio to the new image size
        resized_filter = common_imaging.resize(gay_filter, resized_image.size)

        # Paste the filter onto the frame
        resized_image.paste(resized_filter, (0, 0), resized_filter)

        # Ship it
        await self.save_img_and_send(ctx.author, resized_image, ctx.channel, file_name="gaygaygay.png", things_to_close=(download.image, resized_image, gay_filter, resized_filter))
        del download

    @commands.command(aliases=["inv"])
    async def invert(self, ctx):
        download = await self.get_asset_from_user(ctx)
        if not download:
            return

        # Take the image and resize it with locked aspect ratio to the nearest 250x250
        resized_image = common_imaging.resize_to_nearest(download.image)

        # Invert the resized image
        bands = resized_image.split()
        bands = [ImageOps.invert(b) for b in bands[:-1]] + [bands[-1]]
        resized_image = Image.merge('RGBA', bands)

        # Ship it
        await self.save_img_and_send(ctx.author, resized_image, ctx.channel, file_name="invert.png", things_to_close=(download.image, resized_image))
        del download

    @commands.command(aliases=['hypeify', 'hypeme'])
    async def hypify(self, ctx):
        download = await self.get_asset_from_user(ctx)
        if not download:
            return

        # Take the image and resize it with locked aspect ratio to the nearest 250x250
        resized_image = common_imaging.resize_to_nearest(download.image)

        # Open the filter
        gay_filter = Image.open('content/filters/20hype_arms.png')

        # Take the filter and resize it with unlocked aspect ratio to the new image size
        resized_filter = common_imaging.resize(gay_filter, resized_image.size)

        # Paste the filter onto the frame
        resized_image.paste(resized_filter, (0, -10), resized_filter)

        # Ship it
        await self.save_img_and_send(ctx.author, resized_image, ctx.channel, file_name="20hype_arms.png", things_to_close=(download.image, resized_image, gay_filter, resized_filter))
        del download

    @commands.command()
    async def shake(self, ctx):
        download = await self.get_asset_from_user(ctx)
        if not download:
            return

        def shake_image(image: Image):
            gif = []
            shake_offsets = [
                (-(int(image.width*zoom_level) - image.width) // 2, -(int(image.height*zoom_level) - image.height) // 2),
                (-(int(image.width*zoom_level) - image.width) // 2 + shake_strength, -(int(image.height*zoom_level) - image.height) // 2 + shake_strength),
                (-(int(image.width*zoom_level) - image.width) // 2 + 2 * shake_strength, -(int(image.height*zoom_level) - image.height) // 2),
            ]

            zoomed_image = common_imaging.resize(image, (int(image.width*zoom_level), int(image.height*zoom_level)))

            for idx, offset in enumerate(shake_offsets):
                gif.append(Image.new("RGBA", image.size, (255, 255, 255, 0)))
                gif[-1].paste(zoomed_image, offset, zoomed_image)

                alpha = gif[-1].split()[-1]
                gif[-1] = gif[-1].convert('RGB').convert('P', palette=Image.ADAPTIVE, colors=255)
                mask = Image.eval(alpha, lambda a: 255 if a <= 64 else 0)
                gif[-1].paste(255, mask)

            return gif

        # clamp values
        zoom_level = 1.3
        shake_strength = 5
        zoom_level = min(max(0.5, zoom_level), 3.0)
        shake_strength = min(max(1, shake_strength), 125)

        # Take the image and resize it with locked aspect ratio to the nearest 250x250
        resized_image = common_imaging.resize_to_nearest(download.image)

        # Shake the image
        shaked_emoji = shake_image(resized_image)

        # Ship it
        await self.save_gif_and_send(ctx.author, shaked_emoji, ctx.channel, file_name="shake.gif", things_to_close=(download.image, resized_image) + tuple(shaked_emoji))
        del download

    @commands.command(aliases=['rotate', 'spincc', 'scc', 'rcc', 'rotatecc'])
    async def spin(self, ctx):
        await self._spin(ctx, direction=1)

    @commands.command(aliases=['antirotate', 'spinc', 'sc', 'rc', 'rotatec'])
    async def antispin(self, ctx):
        await self._spin(ctx, direction=-1)

    async def _spin(self, ctx, speed: int=20, direction=1):
        download = await self.get_asset_from_user(ctx)
        if not download:
            return

        def spin_image(image: Image):
            gif = []
            frames = 20
            r_step = 360 / frames
            w = image.size[0]
            h = image.size[1]

            rotated_size = (int((image.size[0] ** 2 + image.size[1] ** 2) ** 0.5), int((image.size[0] ** 2 + image.size[1] ** 2) ** 0.5))

            for i in range(frames):
                gif.append(Image.new("RGBA", rotated_size, (255, 255, 255, 0)))
                gif[-1].paste(image, ((rotated_size[0] - w) // 2, (rotated_size[1] - h) // 2), image)
                gif[-1] = gif[-1].rotate(r_step * i * direction)

                alpha = gif[-1].split()[-1]
                gif[-1] = gif[-1].convert('RGB').convert('P', palette=Image.ADAPTIVE, colors=255)
                mask = Image.eval(alpha, lambda a: 255 if a <= 64 else 0)
                gif[-1].paste(255, mask)

            return gif

        # clamp value
        speed = min(max(20, speed), 1000)

        # Take the image and resize it with locked aspect ratio to the nearest 250x250
        resized_image = common_imaging.resize_to_nearest(download.image)

        # Spin the image
        spinned_image = spin_image(resized_image)

        await self.save_gif_and_send(ctx.author, spinned_image, ctx.channel, file_name="spin.gif", duration=speed, things_to_close=(download.image, resized_image) + tuple(spinned_image))
        del download

    @commands.command(aliases=['hs', 'hypesay'])
    async def hypesign(self, ctx, *, message=""):
        # Verify shit
        limit = 20
        # Clean message: replace new lines with spaces, remove dupped spaces, ensure ascii-128 characters
        message = ''.join(c for c in ' '.join(message.replace('\n', ' ').split(' ')) if ord(c) < 128)
        if message == "":
            return await ctx.channel.send(f"**Error**: No message used. Messages must be between 1 and {limit} characters.")
        elif 0 >= len(message) > limit:
            return await ctx.channel.send(f"**Error**: Messages must be between 1 and {limit} characters.")
        elif has_blacklisted_word(message):
            return await ctx.channel.send(f"**Error**: That message has a blacklisted word in it.")

        # Load the background
        base_hype = Image.open('content/filters/hypesign01.png')

        # Load the middleground
        layer1_hype = Image.open('content/filters/hypesign02.png')
        base_hype.paste(layer1_hype, (0, 0), layer1_hype)

        # Load a new text object for the sign
        text_hype = Image.new('RGBA', (490, 220), (0, 0, 0, 0))
        text_obj = ImageDraw.Draw(text_hype)
        font_size = 160
        font = ImageFont.truetype('content/filters/Krabby_Patty.ttf', font_size)
        done = False
        while True:
            w, h = font.getsize(message)
            if w < text_hype.width - 30:
                text_obj.text((int((text_hype.width - w)//2), int((text_hype.height - h)//2) - 10), message, 'black', font=font)
                done = True
                break
            font_size -= 5
            if font_size <= 80:
                break
            font = ImageFont.truetype('content/filters/Krabby_Patty.ttf', font_size)
        if not done:
            # hard cap, force a split
            if ' ' not in message:
                top = message[:len(message)//2] + "-"
                bottom = message[len(message)//2:]
            else:
                # message || message a
                # a message || message
                words = message.split(' ')
                picked_diff = 10000000
                diff1, diff2 = "", ""
                for idx, word in enumerate(words):
                    first_half = ' '.join(words[:idx])
                    second_half = ' '.join(words[idx:])
                    diff = abs(len(second_half) - len(first_half))
                    if diff < picked_diff:
                        diff1 = first_half
                        diff2 = second_half
                        picked_diff = diff
                top = diff1
                bottom = diff2
            font_size = 110
            while True:
                wt, ht = font.getsize(top)
                wb, hb = font.getsize(bottom)
                if max(wt, wb) < text_hype.width - 30 and ht + hb < text_hype.height - 30:
                    text_obj.text((int((text_hype.width - wt)//2), int((text_hype.height - ht - hb - 10)//2)), top, 'black', font=font)
                    text_obj.text((int((text_hype.width - wb)//2), int((text_hype.height - ht - hb - 10)//2) + ht), bottom, 'black', font=font)
                    done = True
                    break
                font_size -= 5
                if font_size <= 50:
                    break
                font = ImageFont.truetype('content/filters/Krabby_Patty.ttf', font_size)
        if not done:
            return await ctx.channel.send(f"**Error**: That text could not be placed.")

        text_hype = text_hype.rotate(-1.0)
        base_hype.paste(text_hype, (6, 6), text_hype)

        # Load the foreground
        layer2_hype = Image.open('content/filters/hypesign03.png')
        base_hype.paste(layer2_hype, (0, 0), layer2_hype)

        # Ship it
        await self.save_img_and_send(base_hype, ctx.channel, file_name="sign.png")
        base_hype.close()
        layer1_hype.close()
        layer2_hype.close()


def setup(bot):
    bot.add_cog(Filters(bot))
