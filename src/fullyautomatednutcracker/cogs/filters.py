import discord
import io
import re
import typing
import datetime
import requests
import argparse
import random

from discord.ext import commands
from PIL import Image, ImageOps, ImageDraw, ImageFont, ImageFilter

from utils import common_imaging
from utils.argparse_but_better import ArgumentParser
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
            self.frames = [image.convert('RGBA')]
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

        self.parser = ArgumentParser()
        # Size params
        self.parser.add_argument('--size', type=int, default=250, help="Set the square size of an image. Valid between 25px and 5,000px.", choices=[ArgumentParser.Range(25, 5000)])
        self.parser.add_argument('--height', type=int, default=-1, help="Set the height of an image, does not affect width. Overrides --scaled. Valid between 25px and 5,000px.", choices=[ArgumentParser.Range(25, 5000)])
        self.parser.add_argument('--width', type=int, default=-1, help="Set the width of an image, does not affect height. Overrides --scaled. Valid between 25px and 5,000px.", choices=[ArgumentParser.Range(25, 5000)])
        self.parser.add_argument('--unlock-ratio', default=False, help="Scales asset with locked aspect ratio to the size provided. Typically used with --size.", action="store_true")
        self.parser.add_argument('--rotate', type=int, default=0, help="Rotate the source image by a set degree amount. Valid between -360 and 360 degrees.", choices=[ArgumentParser.Range(-360, 360)])
        # General Output
        self.parser.add_argument('--name', type=str, default='out', help="Set the filename of the outputted asset.")
        self.parser.add_argument('--optimize', default=False, help="Optimize the asset palette. Reduces file size at the expense of color range.", action="store_true")
        self.parser.add_argument('--transparency', type=int, default=255, help="Specifies what alpha level is considered transparent. Valid between 0 and 255.", choices=[ArgumentParser.Range(0, 255)])
        # GIF Output
        self.parser.add_argument('--disposal', type=int, default=2, help="Sets the disposal setting. 0 - do whatever, idk, 1 - do not dispose any colors, 2 - restore each frame to the background color, 3 - restore each frame to previous frame color.", choices=[ArgumentParser.Range(0, 3)])
        self.parser.add_argument('--duration', type=int, default=-1, help="The duration in milliseconds each GIF frame should be. Valid between 1ms and 2500ms.", choices=[ArgumentParser.Range(1, 2500)])
        self.parser.add_argument('--no-loop', default=False, help="Specifies whether the GIF should loop or not.", action="store_true")
        # PNG Output
        # None that general doesn't have

        # Custom args for commands here
        # Hypify Command
        self.parser.add_argument('--hype-center-x', type=int, default=0, help="Specifies the x-center point for the hype arms.")
        self.parser.add_argument('--hype-center-y', type=int, default=0, help="Specifies the y-center point for the hype arms.")
        self.parser.add_argument('--hype-scale', type=float, default=1.0, help="Specifies the scale of the hype arms. Valid between 0.1 and 3.0", choices=[ArgumentParser.Range(0.1, 3.0)])
        # Shake Command
        self.parser.add_argument('--shake-distance', type=int, default=5, help="Specifies the maximum shake distance. Valid between 1 and 1000", choices=[ArgumentParser.Range(1, 1000)])
        self.parser.add_argument('--shake-scale', type=float, default=1.3, help="Specifies the scale or zoom of the object before shaken. Valid between 0.1 and 5.0", choices=[ArgumentParser.Range(0.1, 5.0)])
        self.parser.add_argument('--shake-type', type=int, default=0, help="Specifies the shake pattern. 0 - diamond shake, 1 - linear shake, 2 - random shake.")
        # Spin Command
        self.parser.add_argument('--spin-frames', type=int, default=20, help="Specifies the number of rotations in the GIF. Valid between 2 and 60", choices=[ArgumentParser.Range(2, 60)])
        self.parser.add_argument('--spin-no-crop', default=False, help="Specifies whether the GIF should be cropped with a circle or not.", action="store_true")
        self.parser.add_argument('--spin-expand', default=False, help="Specifies whether the GIF should be expanded to ensure it entirely fits in the end result", action="store_true")
        # Blur Command
        self.parser.add_argument('--blur-radius', type=int, default=2, help="Specifies the radius (in pixels) to blur with. Valid between 1 and 100", choices=[ArgumentParser.Range(1, 100)])
        # Among Us Command
        self.parser.add_argument('--crew-color', type=str, default='random', help="Specifies the color of your crew skin, casual name or hex.")
        self.parser.add_argument('--crew-scale', type=float, default=1.0, help="Specifies the scale of the mask that cuts out the face. Valid between 0.1 and 1.0", choices=[ArgumentParser.Range(0.1, 1.0)])
        self.parser.add_argument('--crew-center-x', type=int, default=0, help="Specifies the x-center point for the face-cut mask.")
        self.parser.add_argument('--crew-center-y', type=int, default=0, help="Specifies the y-center point for the face-cut mask.")

    async def wrapped_converter(self, converter, ctx, argument):
        try:
            self.__wrapped_conversion = await converter().convert(ctx, argument)
            return self.__wrapped_conversion
        except:
            return None

    async def get_asset_from_user(self, arguments, ctx, allow_images=True, allow_gifs=False) -> typing.Union[DownloadedAsset, None]:
        content = ' '.join(ctx.message.content.split(' ')[1:]).split()
        content = content[0] if len(content) > 0 else ""
        # Fetch a url
        if content == 'me':
            image_url = ctx.author.avatar_url
        elif len(ctx.message.attachments) > 0:
            image_url = ctx.message.attachments[0].url
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
            image_url = self.user_image_cache[ctx.author.id][0][self.user_image_cache[ctx.author.id][2]]
        else:
            if ctx.author.id in self.user_image_cache:
                del self.user_image_cache[ctx.author.id]
            await ctx.channel.send("**Error**: I could not find an image in your message or in your 15 minute history.")
            return None
        # Sanitize and check it
        headers = requests.head(image_url).headers
        if "Content-Type" not in headers or ("image/png" not in headers["Content-Type"] and "image/jpeg" not in headers["Content-Type"] and "image/webp" not in headers["Content-Type"] and "image/gif" not in headers["Content-Type"]):
            await ctx.channel.send("**Error**: That url does not appear to point to a '.png', '.jpeg/.jpg', '.webp' or '.gif'. These are the only supported image manipulation types.")
            return None
        if "Content-Length" not in headers or not headers["Content-Length"].isnumeric():
            await ctx.channel.send("**Error**: I cannot manipulate this image as the file size is unknown.")
            return None
        if (headers["Content-Type"] == "image/png" or headers["Content-Type"] == "image/jpeg" or headers["Content-Type"] == "image/webp") and int(headers["Content-Length"]) > 1500000:
            await ctx.channel.send("**Error**: The image is too big! It must be less than 1.5 MB.")
            return None
        if headers["Content-Type"] == "image/gif" and int(headers["Content-Length"]) > 15000000:
            await ctx.channel.send("**Error**: The gif is too big! It must be less than 15 MB.")
            return None
        try:
            if not allow_gifs and headers["Content-Type"] == "image/gif":
                ctype = "image/png"
            elif not allow_images and (headers["Content-Type"] == "image/png" or headers["Content-Type"] == "image/jpeg" or  headers["Content-Type"] == "image/webp"):
                ctype = "image/gif"
            else:
                ctype = headers["Content-Type"]
            download = common_imaging.image_from_url(image_url, ctype)
            if ctype == "image/gif" and arguments.duration == -1:
                arguments.duration = download.info['duration'] if 'duration' in download.info else 20
            return DownloadedAsset(download, ctype == "image/gif")
        except:
            await ctx.channel.send("**Error**: I could not download or convert that file!")
            return None

    async def get_args_from_message(self, ctx):
        args = ctx.message.content
        try:
            return self.parser.parse_known_args(args.split())[0]  # stupid af argparse
        except argparse.ArgumentError as ex:
            await ctx.channel.send(f"**Error**: Argument `{ex.argument_name}` could not be parsed. Either the value is out of range or no value was specified.\n`{ex.argument_name} help` - {self.parser._option_string_actions[ex.argument_name].help}")
            return None

    async def save_img_and_send(self, arguments, for_user: discord.User, channel: discord.TextChannel, img: Image, file_name="filter", things_to_close: tuple=()):
        bytes_fp = io.BytesIO()
        img.save(bytes_fp, format="PNG")
        bytes_fp.seek(0)
        message = await channel.send(file=discord.File(bytes_fp, (file_name if arguments.name == "out" else arguments.name) + ".png"))

        if for_user.id not in self.user_image_cache:
            self.user_image_cache[for_user.id] = [[], None, -1]
        self.user_image_cache[for_user.id][1] = datetime.datetime.now().timestamp()
        if self.user_image_cache[for_user.id][2] != len(self.user_image_cache[for_user.id][0]) - 1:
            self.user_image_cache[for_user.id][0] = self.user_image_cache[for_user.id][0][:self.user_image_cache[for_user.id][2] + 1]
        self.user_image_cache[for_user.id][0].append(message.attachments[0].url)
        self.user_image_cache[for_user.id][2] = len(self.user_image_cache[for_user.id][0]) - 1

        for ttc in things_to_close:
            ttc.close()

    async def save_gif_and_send(self, arguments, for_user: discord.User, channel: discord.TextChannel, imgs: [Image], file_name="filter", things_to_close: tuple=()):
        bytes_fp = io.BytesIO()
        imgs[0].save(bytes_fp, format="GIF", optimize=arguments.optimize, save_all=True, append_images=imgs[1:],
                     loop=1 if arguments.no_loop else 0, duration=arguments.duration, transparency=arguments.transparency, disposal=arguments.disposal)
        bytes_fp.seek(0)
        message = await channel.send(file=discord.File(bytes_fp, (file_name if arguments.name == "out" else arguments.name) + ".gif"))

        if for_user.id not in self.user_image_cache:
            self.user_image_cache[for_user.id] = [[], None, -1]
        self.user_image_cache[for_user.id][1] = datetime.datetime.now().timestamp()
        if self.user_image_cache[for_user.id][2] != len(self.user_image_cache[for_user.id][0]) - 1:
            self.user_image_cache[for_user.id][0] = self.user_image_cache[for_user.id][0][:self.user_image_cache[for_user.id][2] + 1]
        self.user_image_cache[for_user.id][0].append(message.attachments[0].url)
        self.user_image_cache[for_user.id][2] = len(self.user_image_cache[for_user.id][0]) - 1

        for ttc in things_to_close:
            ttc.close()

    @staticmethod
    def do_arg_resize(image: Image, arguments) -> Image:
        if arguments.unlock_ratio:
            width = arguments.size if arguments.width == -1 else arguments.width
            height = arguments.size if arguments.height == -1 else arguments.height
            return common_imaging.resize(image, (width, height))
        else:
            if arguments.height != -1:
                nearest_size = arguments.height
            elif arguments.width != -1:
                nearest_size = arguments.width
            else:
                nearest_size = arguments.size
            resized_image = common_imaging.resize_to_nearest(image, nearest_size)
            return resized_image.rotate(arguments.rotate)

    @commands.command()
    async def image(self, ctx):
        f"""asdasd{self.bot.user.name}"""
        arguments = await self.get_args_from_message(ctx)
        if not arguments:
            return
        download = await self.get_asset_from_user(arguments, ctx, allow_gifs=True)
        if not download:
            return
        for idx, frame in enumerate(download.frames):
            # Take the image and resize it with locked aspect ratio to the nearest 250x250
            download.frames[idx] = self.do_arg_resize(frame, arguments)

        # Ship it
        if download.is_gif:
            await self.save_gif_and_send(arguments, ctx.author, ctx.channel, download.frames, file_name="image")
        else:
            await self.save_img_and_send(arguments, ctx.author, ctx.channel, download.frames[0], file_name="image")
        del download

    @commands.command(aliases=["inv"])
    async def invert(self, ctx):
        arguments = await self.get_args_from_message(ctx)
        if not arguments:
            return
        download = await self.get_asset_from_user(arguments, ctx, allow_gifs=True)
        if not download:
            return

        for idx, frame in enumerate(download.frames):
            # Take the image and resize it with locked aspect ratio to the nearest 250x250
            download.frames[idx] = self.do_arg_resize(frame, arguments)

            # Invert the resized image
            bands = download.frames[idx].split()
            bands = [ImageOps.invert(b) for b in bands[:-1]] + [bands[-1]]
            download.frames[idx] = Image.merge('RGBA', bands)

        # Ship it
        if download.is_gif:
            await self.save_gif_and_send(arguments, ctx.author, ctx.channel, download.frames, file_name="invert", things_to_close=(download.image,))
        else:
            await self.save_img_and_send(arguments, ctx.author, ctx.channel, download.frames[0], file_name="invert", things_to_close=(download.image,))
        del download

    @commands.command(aliases=['hypeify', 'hypeme'])
    async def hypify(self, ctx):
        arguments = await self.get_args_from_message(ctx)
        if not arguments:
            return
        download = await self.get_asset_from_user(arguments, ctx)
        if not download:
            return

        # Take the image and resize it with locked aspect ratio to the nearest 250x250
        resized_image = self.do_arg_resize(download.image, arguments)

        # Open the filter
        arms_filter = Image.open('content/filters/20hype_arms.png')

        # Take the filter and resize it with unlocked aspect ratio to the new image size
        resized_filter = common_imaging.resize(arms_filter, (int(resized_image.height * arguments.hype_scale), int(resized_image.width * arguments.hype_scale)))
        center_point = (int((resized_image.height - resized_filter.height) // 2) + arguments.hype_center_x, int((resized_image.width - resized_filter.width) // 2) + arguments.hype_center_y)

        # Paste the filter onto the frame
        resized_image.paste(resized_filter, center_point, resized_filter)

        # Ship it
        await self.save_img_and_send(arguments, ctx.author, ctx.channel, resized_image, file_name="20hype_arms", things_to_close=(download.image, resized_image, arms_filter, resized_filter))
        del download

    @commands.command()
    async def shake(self, ctx):
        arguments = await self.get_args_from_message(ctx)
        if not arguments:
            return
        download = await self.get_asset_from_user(arguments, ctx)
        if not download:
            return

        def shake_image(image: Image):
            gif = []
            diamond_shake_offsets = [
                (-(int(image.width*arguments.shake_scale) - image.width) // 2, -(int(image.height*arguments.shake_scale) - image.height) // 2),
                (-(int(image.width*arguments.shake_scale) - image.width) // 2 + arguments.shake_distance, -(int(image.height*arguments.shake_scale) - image.height) // 2 + arguments.shake_distance),
                (-(int(image.width*arguments.shake_scale) - image.width) // 2 + 2 * arguments.shake_distance, -(int(image.height*arguments.shake_scale) - image.height) // 2),
            ]
            linear_shake_offsets = [
                (-(int(image.width*arguments.shake_scale) - image.width) // 2 - arguments.shake_distance, -(int(image.height*arguments.shake_scale) - image.height) // 2),
                (-(int(image.width*arguments.shake_scale) - image.width) // 2, -(int(image.height*arguments.shake_scale) - image.height) // 2),
                (-(int(image.width*arguments.shake_scale) - image.width) // 2 + arguments.shake_distance, -(int(image.height*arguments.shake_scale) - image.height) // 2),
                (-(int(image.width*arguments.shake_scale) - image.width) // 2, -(int(image.height*arguments.shake_scale) - image.height) // 2),

            ]
            random_shake_offsets = [
                (-(int(image.width*arguments.shake_scale) - image.width) // 2, -(int(image.height*arguments.shake_scale) - image.height) // 2),
                (-(int(image.width*arguments.shake_scale) - image.width) // 2 + int((random.random() * 2 - 1) * arguments.shake_distance), -(int(image.height*arguments.shake_scale) - image.height) // 2 + int((random.random() * 2 - 1) * arguments.shake_distance)),
                (-(int(image.width*arguments.shake_scale) - image.width) // 2 + int((random.random() * 2 - 1) * arguments.shake_distance), -(int(image.height*arguments.shake_scale) - image.height) // 2 + int((random.random() * 2 - 1) * arguments.shake_distance)),
            ]

            if arguments.shake_type == 1:
                shake_offsets = linear_shake_offsets
            elif arguments.shake_type == 2:
                shake_offsets = random_shake_offsets
            else:  # if arguments.shake_type == 0:
                shake_offsets = diamond_shake_offsets

            zoomed_image = common_imaging.resize(image, (int(image.width*arguments.shake_scale), int(image.height*arguments.shake_scale)))

            for idx, offset in enumerate(shake_offsets):
                gif.append(Image.new("RGBA", image.size, (255, 255, 255, 0)))
                gif[-1].paste(zoomed_image, offset, zoomed_image)

                alpha = gif[-1].split()[-1]
                gif[-1] = gif[-1].convert('RGB').convert('P', palette=Image.ADAPTIVE, colors=255)
                mask = Image.eval(alpha, lambda a: 255 if a <= 64 else 0)
                gif[-1].paste(255, mask)

            return gif

        # Take the image and resize it with locked aspect ratio to the nearest 250x250
        resized_image = self.do_arg_resize(download.image, arguments)

        # Shake the image
        shaked_emoji = shake_image(resized_image)

        # Set the max speed if it wasn't set
        if arguments.duration == -1:
            arguments.duration = 20

        # Ship it
        await self.save_gif_and_send(arguments, ctx.author, ctx.channel, shaked_emoji, file_name="shake", things_to_close=(download.image, resized_image) + tuple(shaked_emoji))
        del download

    @commands.command(aliases=['rotate', 'spincc', 'scc', 'rcc', 'rotatecc', 'spinleft'])
    async def spin(self, ctx):
        await self._spin(ctx, direction=1)

    @commands.command(aliases=['antirotate', 'spinc', 'sc', 'rc', 'rotatec', 'spinright'])
    async def antispin(self, ctx):
        await self._spin(ctx, direction=-1)

    async def _spin(self, ctx, direction):
        arguments = await self.get_args_from_message(ctx)
        if not arguments:
            return
        download = await self.get_asset_from_user(arguments, ctx)
        if not download:
            return

        def spin_image(image: Image):
            gif = []
            frames = arguments.spin_frames
            r_step = 360 / frames
            w = image.width
            h = image.height

            if arguments.spin_expand:
                rotated_size = (int((w ** 2 + h ** 2) ** 0.5), int((w ** 2 + h ** 2) ** 0.5))
            else:
                if arguments.spin_no_crop:
                    rotated_size = image.size
                else:
                    rotated_size = (min(w, h), min(w, h))

            if not arguments.spin_no_crop:
                spin_mask = Image.open('content/filters/pfp_mask.png')
                resized_spin_mask = common_imaging.resize(spin_mask, (min(rotated_size[0], rotated_size[1]), min(rotated_size[0], rotated_size[1])))

            for i in range(frames):
                gif.append(Image.new("RGBA", rotated_size, (255, 255, 255, 0)))
                if arguments.spin_no_crop:
                    gif[-1].paste(image, ((rotated_size[0] - w) // 2, (rotated_size[1] - h) // 2), image)
                else:
                    # guaranteed to be a square image here
                    squared = Image.new("RGBA", rotated_size)
                    squared.paste(image, ((rotated_size[0] - w) // 2, (rotated_size[1] - h) // 2), image)
                    masked = Image.new("RGBA", rotated_size)
                    masked.paste(resized_spin_mask, (0, 0), squared)
                    gif[-1].paste(squared, ((rotated_size[0] - masked.width) // 2, (rotated_size[1] - masked.height) // 2), masked)

                gif[-1] = gif[-1].rotate(r_step * i * direction)

                alpha = gif[-1].split()[-1]
                gif[-1] = gif[-1].convert('RGB').convert('P', palette=Image.ADAPTIVE, colors=255)
                mask = Image.eval(alpha, lambda a: 255 if a <= 64 else 0)
                gif[-1].paste(255, mask)

            return gif

        # Take the image and resize it with locked aspect ratio to the nearest 250x250
        resized_image = self.do_arg_resize(download.image, arguments)

        # Spin the image
        spun_image = spin_image(resized_image)

        # Set the max speed if it wasn't set
        if arguments.duration == -1:
            arguments.duration = 20

        await self.save_gif_and_send(arguments, ctx.author, ctx.channel, spun_image, file_name="spin", things_to_close=(download.image, resized_image) + tuple(spun_image))
        del download

    @commands.command(aliases=['hs', 'hypesay'])
    async def hypesign(self, ctx, *, message=""):
        arguments = await self.get_args_from_message(ctx)
        if not arguments:
            return
        # Verify shit
        limit = 20
        # Clean message: replace new lines with spaces, remove dupped spaces, ensure ascii-128 characters
        message = ''.join(c for c in ' '.join(message.replace('\n', ' ').split(' ')) if ord(c) < 128)
        if '-' in message:
            message = message[0:message.index('-')].strip()
        if message == "":
            return await ctx.channel.send(f"**Error**: No message used. Messages must be between 1 and {limit} characters.")
        elif len(message) <= 0 or len(message) > limit:
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

        # Override the default size argument
        if arguments.size != 250 or arguments.height != -1 or arguments.width != -1:
            base_hype = self.do_arg_resize(base_hype, arguments)

        # Ship it
        await self.save_img_and_send(arguments, ctx.author, ctx.channel, base_hype, file_name="sign", things_to_close=(base_hype, layer1_hype, layer2_hype))

    @commands.command(aliases=['horizontal', 'hflip', 'hswap'])
    async def flip(self, ctx):
        arguments = await self.get_args_from_message(ctx)
        if not arguments:
            return
        download = await self.get_asset_from_user(arguments, ctx, allow_gifs=True)
        if not download:
            return
        for idx, frame in enumerate(download.frames):
            # Take the image and resize it with locked aspect ratio to the nearest 250x250
            download.frames[idx] = self.do_arg_resize(frame, arguments)
            download.frames[idx] = download.frames[idx].transpose(Image.FLIP_LEFT_RIGHT)

        # Ship it
        if download.is_gif:
            await self.save_gif_and_send(arguments, ctx.author, ctx.channel, download.frames, file_name="flip", things_to_close=(download.image,))
        else:
            await self.save_img_and_send(arguments, ctx.author, ctx.channel, download.frames[0], file_name="flip", things_to_close=(download.image,))
        del download

    @commands.command(aliases=['vertical', 'verticle', 'vflip', 'vswap'])
    async def swap(self, ctx):
        arguments = await self.get_args_from_message(ctx)
        if not arguments:
            return
        download = await self.get_asset_from_user(arguments, ctx, allow_gifs=True)
        if not download:
            return
        for idx, frame in enumerate(download.frames):
            # Take the image and resize it with locked aspect ratio to the nearest 250x250
            download.frames[idx] = self.do_arg_resize(frame, arguments)
            download.frames[idx] = download.frames[idx].transpose(Image.FLIP_TOP_BOTTOM)

        # Ship it
        if download.is_gif:
            await self.save_gif_and_send(arguments, ctx.author, ctx.channel, download.frames, file_name="swap", things_to_close=(download.image,))
        else:
            await self.save_img_and_send(arguments, ctx.author, ctx.channel, download.frames[0], file_name="swap", things_to_close=(download.image,))
        del download

    @commands.command(aliases=['hm', 'haah'])
    async def hmirror(self, ctx):
        arguments = await self.get_args_from_message(ctx)
        if not arguments:
            return
        download = await self.get_asset_from_user(arguments, ctx, allow_gifs=True)
        if not download:
            return
        for idx, frame in enumerate(download.frames):
            # Take the image and resize it with locked aspect ratio to the nearest 250x250
            left = self.do_arg_resize(frame, arguments)
            new_image = Image.new('RGBA', left.size)
            left = left.crop((0, 0, left.width // 2, left.height))
            right = left.transpose(Image.FLIP_LEFT_RIGHT)

            new_image.paste(left, (0, 0), left)
            new_image.paste(right, (left.width, 0), right)

            download.frames[idx] = new_image

        # Ship it
        if download.is_gif:
            await self.save_gif_and_send(arguments, ctx.author, ctx.channel, download.frames, file_name="hmirror", things_to_close=(download.image,))
        else:
            await self.save_img_and_send(arguments, ctx.author, ctx.channel, download.frames[0], file_name="hmirror", things_to_close=(download.image,))
        del download

    @commands.command(aliases=['ihm', 'waaw'])
    async def invhmirror(self, ctx):
        arguments = await self.get_args_from_message(ctx)
        if not arguments:
            return
        download = await self.get_asset_from_user(arguments, ctx, allow_gifs=True)
        if not download:
            return
        for idx, frame in enumerate(download.frames):
            # Take the image and resize it with locked aspect ratio to the nearest 250x250
            right = self.do_arg_resize(frame, arguments)
            new_image = Image.new('RGBA', right.size)
            right = right.crop((right.width // 2, 0, right.width, right.height))
            left = right.transpose(Image.FLIP_LEFT_RIGHT)

            new_image.paste(left, (0, 0), left)
            new_image.paste(right, (left.width, 0), right)

            download.frames[idx] = new_image

        # Ship it
        if download.is_gif:
            await self.save_gif_and_send(arguments, ctx.author, ctx.channel, download.frames, file_name="invhmirror", things_to_close=(download.image,))
        else:
            await self.save_img_and_send(arguments, ctx.author, ctx.channel, download.frames[0], file_name="invhmirror", things_to_close=(download.image,))
        del download

    @commands.command(aliases=['vm', 'hooh'])
    async def vmirror(self, ctx):
        arguments = await self.get_args_from_message(ctx)
        if not arguments:
            return
        download = await self.get_asset_from_user(arguments, ctx, allow_gifs=True)
        if not download:
            return
        for idx, frame in enumerate(download.frames):
            # Take the image and resize it with locked aspect ratio to the nearest 250x250
            bottom = self.do_arg_resize(frame, arguments)
            new_image = Image.new('RGBA', bottom.size)
            bottom = bottom.crop((0, bottom.height // 2, bottom.width, bottom.height))
            top = bottom.transpose(Image.FLIP_TOP_BOTTOM)

            new_image.paste(top, (0, 0), top)
            new_image.paste(bottom, (0, top.height), bottom)

            download.frames[idx] = new_image

        # Ship it
        if download.is_gif:
            await self.save_gif_and_send(arguments, ctx.author, ctx.channel, download.frames, file_name="vmirror", things_to_close=(download.image,))
        else:
            await self.save_img_and_send(arguments, ctx.author, ctx.channel, download.frames[0], file_name="vmirror", things_to_close=(download.image,))
        del download

    @commands.command(aliases=['ivm', 'woow'])
    async def invvmirror(self, ctx):
        arguments = await self.get_args_from_message(ctx)
        if not arguments:
            return
        download = await self.get_asset_from_user(arguments, ctx, allow_gifs=True)
        if not download:
            return
        for idx, frame in enumerate(download.frames):
            # Take the image and resize it with locked aspect ratio to the nearest 250x250
            top = self.do_arg_resize(frame, arguments)
            new_image = Image.new('RGBA', top.size)
            top = top.crop((0, 0, top.width, top.height // 2))
            bottom = top.transpose(Image.FLIP_TOP_BOTTOM)

            new_image.paste(top, (0, 0), top)
            new_image.paste(bottom, (0, top.height), bottom)

            download.frames[idx] = new_image

        # Ship it
        if download.is_gif:
            await self.save_gif_and_send(arguments, ctx.author, ctx.channel, download.frames, file_name="invvmirror", things_to_close=(download.image,))
        else:
            await self.save_img_and_send(arguments, ctx.author, ctx.channel, download.frames[0], file_name="invvmirror", things_to_close=(download.image,))
        del download

    @commands.command(aliases=['rewind'])
    async def reverse(self, ctx):
        arguments = await self.get_args_from_message(ctx)
        if not arguments:
            return
        download = await self.get_asset_from_user(arguments, ctx, allow_gifs=True, allow_images=False)
        if not download:
            return
        download.frames.reverse()
        download.image = download.frames[0]
        for idx, frame in enumerate(download.frames):
            # Take the image and resize it with locked aspect ratio to the nearest 250x250
            download.frames[idx] = self.do_arg_resize(frame, arguments)

        # Ship it
        await self.save_gif_and_send(arguments, ctx.author, ctx.channel, download.frames, file_name="reverse", things_to_close=(download.image,))
        del download

    @commands.command(aliases=['gaussian'])
    async def blur(self, ctx):
        arguments = await self.get_args_from_message(ctx)
        if not arguments:
            return
        download = await self.get_asset_from_user(arguments, ctx, allow_gifs=True)
        if not download:
            return
        for idx, frame in enumerate(download.frames):
            # Take the image and resize it with locked aspect ratio to the nearest 250x250
            download.frames[idx] = self.do_arg_resize(frame, arguments).filter(ImageFilter.GaussianBlur(radius=arguments.blur_radius))

        # Ship it
        if download.is_gif:
            await self.save_gif_and_send(arguments, ctx.author, ctx.channel, download.frames, file_name="blur", things_to_close=(download.image,))
        else:
            await self.save_img_and_send(arguments, ctx.author, ctx.channel, download.frames[0], file_name="blur", things_to_close=(download.image,))
        del download

    @commands.command(aliases=['convolve', 'convolutionize'])
    async def kernel(self, ctx):
        arguments = await self.get_args_from_message(ctx)
        if not arguments:
            return
        download = await self.get_asset_from_user(arguments, ctx)
        if not download:
            return

        download.image = self.do_arg_resize(download.image, arguments)
        backdrop = Image.new('RGB', download.image.size, (0, 0, 0))
        backdrop.paste(download.image, (0, 0), download.image)
        kernel_image = backdrop.filter(ImageFilter.Kernel(
            (3, 3),
            (-1, -1, -1, -1, 11, -2, -2, -2, -2),
            1
        ))
        download.image = kernel_image

        # Ship it
        await self.save_img_and_send(arguments, ctx.author, ctx.channel, download.image, file_name="kernel", things_to_close=(download.image, backdrop, kernel_image))
        del download

    @commands.command()
    async def rgbsplit(self, ctx):
        arguments = await self.get_args_from_message(ctx)
        if not arguments:
            return
        download = await self.get_asset_from_user(arguments, ctx)
        if not download:
            return

        download.image = self.do_arg_resize(download.image, arguments)

        r, g, b, a = download.image.split()
        black = Image.new('L', download.image.size, 0)
        r = Image.merge('RGBA', [r, black, black, a])
        g = Image.merge('RGBA', [black, g, black, a])
        b = Image.merge('RGBA', [black, black, b, a])

        r.putalpha(128)
        g.putalpha(128)
        b.putalpha(128)

        new_image = Image.new('RGBA', download.image.size, (0, 0, 0, 0))
        new_image.paste(r, (-25, -25), r)
        new_image.paste(g, (0, 0), g)
        new_image.paste(b, (25, 25), b)

        download.image = new_image

        # Ship it
        await self.save_img_and_send(arguments, ctx.author, ctx.channel, download.image, file_name="rgbsplit", things_to_close=(download.image, new_image, r, g, b, black))
        del download

    @commands.command(aliases=['amung', 'amongus', 'amungus'])
    async def among(self, ctx):
        arguments = await self.get_args_from_message(ctx)
        if not arguments:
            return
        download = await self.get_asset_from_user(arguments, ctx)
        if not download:
            return

        # Open the filter
        face_mask = Image.open('content/filters/among01.png')
        color_mask = Image.open('content/filters/among02.png')
        crew_border = Image.open('content/filters/among03.png')

        # Get a color
        def is_hex_string(c):
            try:
                c = c.replace('#', '')
                if len(c) == 3 or len(c) == 6:
                    int(c, 16)
                    return c
                else:
                    return None
            except:
                return None
        color = int(common_imaging.hex_string_from_color_name(arguments.crew_color) or is_hex_string(arguments.crew_color) or common_imaging.random_hex_color(), 16)
        rgba = ((color >> 16) & 255, (color >> 8) & 255, color & 255, 255)

        # Create the crew color and the mask for it
        crew_filter = Image.new('RGBA', color_mask.size, (0, 0, 0, 0))
        color_filter = Image.new('RGBA', color_mask.size, rgba)
        crew_filter.paste(color_filter, (0, 0), color_mask)

        # Create a face mask
        face_mask.thumbnail(download.image.size)
        resized_face_mask = face_mask
        resized_face_mask = common_imaging.resize(resized_face_mask, (int(resized_face_mask.width * arguments.crew_scale), int(resized_face_mask.height * arguments.crew_scale)))

        placed_face_mask = Image.new('RGBA', download.size, (0, 0, 0, 0))
        min_x = min(download.width - resized_face_mask.width, max(0, int((download.width - resized_face_mask.width) // 2) + arguments.crew_center_x))
        min_y = min(download.height - resized_face_mask.height, max(0, int((download.height - resized_face_mask.height) // 2) + arguments.crew_center_y))
        placed_face_mask.paste(resized_face_mask, (min_x, min_y), resized_face_mask)

        extracted_face_mask = Image.new('RGBA', download.size, (0, 0, 0, 0))
        extracted_face_mask.paste(download.image, (0, 0), placed_face_mask)
        extracted_face_mask = extracted_face_mask.crop((min_x, min_y, min_x + resized_face_mask.width, min_y + resized_face_mask.height))
        extracted_face_mask = common_imaging.resize(extracted_face_mask, (604, 454))
        crew_filter.paste(extracted_face_mask, (63, 254), extracted_face_mask)

        # Place the border
        crew_filter.paste(crew_border, (0, 0), crew_border)

        # Take the filter and resize it with unlocked aspect ratio to the new image size
        crew_filter = self.do_arg_resize(crew_filter, arguments)

        # Ship it
        await self.save_img_and_send(arguments, ctx.author, ctx.channel, crew_filter, file_name="amongus", things_to_close=(download.image, crew_filter, color_filter, crew_border, color_mask, face_mask))
        del download

    @commands.command(aliases=['u'])
    async def undo(self, ctx, amount: int=1):
        if ctx.author.id not in self.user_image_cache:
            await ctx.channel.send("Nothing to undo.")
        else:
            self.user_image_cache[ctx.author.id][2] = max(0, self.user_image_cache[ctx.author.id][2] - amount)
            await ctx.channel.send(self.user_image_cache[ctx.author.id][0][self.user_image_cache[ctx.author.id][2]])

    @commands.command(aliases=['r'])
    async def redo(self, ctx, amount: int=1):
        if ctx.author.id not in self.user_image_cache:
            await ctx.channel.send("Nothing to redo.")
        else:
            self.user_image_cache[ctx.author.id][2] = min(len(self.user_image_cache[ctx.author.id][0]) - 1, self.user_image_cache[ctx.author.id][2] + amount)
            await ctx.channel.send(self.user_image_cache[ctx.author.id][0][self.user_image_cache[ctx.author.id][2]])

    @commands.command(aliases=['br'])
    async def backgroundresize(self, ctx):
        arguments = await self.get_args_from_message(ctx)
        if not arguments:
            return
        download = await self.get_asset_from_user(arguments, ctx, allow_gifs=False)
        if not download:
            return
        h = 300
        w = 950
        resized_download = common_imaging.resize(download.image, (w, h))
        await self.save_img_and_send(arguments, ctx.author, ctx.channel,resized_download, file_name='Resized_Background', things_to_close=(resized_download, download.image))

    async def apply_mask(self, ctx, image):
        arguments = await self.get_args_from_message(ctx)
        if not arguments:
            return
        download = await self.get_asset_from_user(arguments, ctx, allow_gifs=True)
        if not download:
            return

        # Open the filter
        filter = Image.open(f'content/filters/{image}')
        resized_filter = None

        for idx, frame in enumerate(download.frames):
            # Take the image and resize it with locked aspect ratio to the nearest 250x250
            download.frames[idx] = self.do_arg_resize(frame, arguments)
            if not resized_filter:
                resized_filter = common_imaging.resize(filter, download.frames[idx].size)
            # Paste the filter onto the frame
            download.frames[idx].paste(resized_filter, (0, 0), resized_filter)

        # Ship it
        if download.is_gif:
            await self.save_gif_and_send(arguments, ctx.author, ctx.channel, download.frames, file_name=image.split(".")[0], things_to_close=(download.image, filter, resized_filter))
        else:
            await self.save_img_and_send(arguments, ctx.author, ctx.channel, download.frames[0], file_name=image.split(".")[0], things_to_close=(download.image, filter, resized_filter))
        del download

    @commands.command(aliases=['ace','ase'])
    async def asexual(self, ctx):
        await self.apply_mask(ctx, "asexual_flag_overlay.png")

    @commands.command(aliases=['bisexual'])
    async def bi(self, ctx):
        await self.apply_mask(ctx, "bi_flag_overlay.png")

    @commands.command(aliases=['nonbinary','nb'])
    async def enby(self):
        await self.apply_mask(ctx, "enby_flag_overlay.png")

    @commands.command(aliases=['gf','genf'])
    async def gender_fluid(self, ctx):
        await self.apply_mask(ctx, "gender_fluid_flag_overlay.png")

    @commands.command(aliases=['gq','genq'])
    async def gender_queer(self, ctx):
        await self.apply_mask(ctx, "gender_queer_flag_overlay.png")

    @commands.command(aliases=['les'])
    async def lesbian(self, ctx):
        await self.apply_mask(ctx, "lesbian_flag_overlay.png")

    @commands.command(aliases=['pansexual'])
    async def pan(self, ctx):
        await self.apply_mask(ctx, "pan_flag_overlay.png")

    @commands.command(aliases=['poly'])
    async def polysexual(self, ctx):
        await self.apply_mask(ctx, "polysexual_flag_overlay.png")

    @commands.command(aliases=["tr", "transgender"])
    async def trans(self, ctx):
        await self.apply_mask(ctx, "trans_flag_mask.png")

    @commands.command(aliases=["comrade"])
    async def commie(self):
        await self.apply_mask("commie.png")

    @commands.command(aliases=["gay", "rainbow", "mod"])
    async def gaygaygay(self, ctx):
        await self.apply_mask(ctx, "gaygaygay.png")

def setup(bot):
    bot.add_cog(Filters(bot))
