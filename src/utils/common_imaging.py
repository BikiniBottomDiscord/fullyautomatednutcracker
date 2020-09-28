import io
import requests
import random

from PIL import Image, ImageDraw, ImageFont


def resize(im, size):
    bands = im.split()
    bands = [b.resize(size, Image.LINEAR) for b in bands]
    return Image.merge('RGBA', bands)


def resize_to_nearest(image, square_size):
    bands = image.split()
    width_diff = abs(image.width - square_size)
    height_diff = abs(image.height - square_size)
    if height_diff > width_diff:
        size = (square_size, image.height * square_size // image.width)
    else:
        size = (image.width * square_size // image.height, square_size)
    bands = [b.resize(size, Image.LINEAR) for b in bands]
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


def hex_string_from_color_name(color_name: str):
    return hex_colors[color_name.lower()] if color_name.lower() in hex_colors else None


def random_hex_color():
    return random.choice(list(hex_colors.values()))


hex_colors = {
    "amaranth": "E52B50",
    "amber": "FFBF00",
    "amethyst": "9966CC",
    "apricot": "FBCEB1",
    "aquamarine": "7FFFD4",
    "azure": "007FFF",
    "babyblue": "89CFF0",
    "beige": "F5F5DC",
    "brick": "CB4154",
    "black": "000000",
    "blue": "0000FF",
    "bluegreen": "0095B6",
    "blueviolet": "8A2BE2",
    "blush": "DE5D83",
    "bronze": "CD7F32",
    "brown": "964B00",
    "burgundy": "800020",
    "byzantium": "702963",
    "barmine": "960018",
    "berise": "DE3163",
    "cerulean": "007BA7",
    "champagne": "F7E7CE",
    "chartreuse": "7FFF00",
    "chocolate": "7B3F00",
    "cobalt": "0047AB",
    "coffee": "6F4E37",
    "copper": "B87333",
    "coral": "FF7F50",
    "crimson": "DC143C",
    "cyan": "00FFFF",
    "desert": "EDC9Af",
    "electric": "7DF9FF",
    "emerald": "50C878",
    "erin": "00FF3F",
    "gold": "FFD700",
    "gray": "808080",
    "grey": "808080",
    "green": "008000",
    "harlequin": "3FFF00",
    "indigo": "4B0082",
    "ivory": "FFFFF0",
    "jade": "00A86B",
    "jungle": "29AB87",
    "lavender": "B57EDC",
    "lemon": "FFF700",
    "lilac": "C8A2C8",
    "lime": "BFFF00",
    "magenta": "FF00FF",
    "rose": "FF00AF",
    "maroon": "800000",
    "mauve": "E0B0FF",
    "navy": "000080",
    "ochre": "CC7722",
    "olive": "808000",
    "orange": "FF6600",
    "orangered": "FF4500",
    "orchid": "DA70D6",
    "peach": "FFE5B4",
    "pear": "D1E231",
    "periwinkle": "CCCCFF",
    "persian": "1C39BB",
    "pink": "FD6C9E",
    "plum": "8E4585",
    "prussian": "003153",
    "puce": "CC8899",
    "purple": "800080",
    "raspberry": "E30B5C",
    "red": "FF0000",
    "redviolet": "C71585",
    "ruby": "E0115F",
    "salmon": "FA8072",
    "sangria": "92000A",
    "sapphire": "0F52BA",
    "scarlet": "FF2400",
    "silver": "C0C0C0",
    "slate": "708090",
    "spring": "A7FC00",
    "tan": "D2B48C",
    "taupe": "483C32",
    "teal": "008080",
    "turquoise": "40E0D0",
    "ultramarine": "3F00FF",
    "violet": "7F00FF",
    "viridian": "40826D",
    "white": "FFFFFF",
    "yellow": "FFFF00",
}
