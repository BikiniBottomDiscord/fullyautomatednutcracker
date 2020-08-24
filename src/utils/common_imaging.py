import io
import requests

from PIL import Image, ImageDraw, ImageFont


def resize(im, size):
    bands = im.split()
    bands = [b.resize((size, size), Image.LINEAR) for b in bands]
    return Image.merge('RGBA', bands)


def image_from_url(url, content_type):
    try:
        response = requests.get(url)
        img = Image.open(io.BytesIO(response.content))
        if content_type != 'image/gif':
            img = img.convert('RGBA')
        return img
    except Exception as ex:
        return None


def text_outline(pos: tuple, content: str, draw: ImageDraw, font: ImageFont, base_color: str, outline_color: str="black", outline_width: int=1):
    draw.text((pos[0] - outline_width, pos[1] - outline_width), content, outline_color, font=font)
    draw.text((pos[0], pos[1] - outline_width), content, outline_color, font=font)
    draw.text((pos[0] + outline_width, pos[1] - outline_width), content, outline_color, font=font)
    draw.text((pos[0] + outline_width, pos[1]), content, outline_color, font=font)
    draw.text((pos[0] + outline_width, pos[1] + outline_width), content, outline_color, font=font)
    draw.text((pos[0], pos[1] + outline_width), content, outline_color, font=font)
    draw.text((pos[0] - outline_width, pos[1] + outline_width), content, outline_color, font=font)
    draw.text((pos[0] - outline_width, pos[1]), content, outline_color, font=font)
    draw.text(pos, content, base_color, font=font)


def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i+lv//3], 16) for i in range(0, lv, lv//3))
