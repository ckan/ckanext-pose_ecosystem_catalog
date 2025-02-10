import wcag_contrast_ratio as contrast
from webcolors import name_to_hex, hex_to_rgb


def get_rgb_from_color(color):
    try:
        hex_color = name_to_hex(color)
    except ValueError:
        hex_color = color

    rgb_normalized = [round(float(float(i) / 255), 2) for i in hex_to_rgb(hex_color)]
    return rgb_normalized


def get_contrast(color_1, color_2):

    return contrast.rgb(get_rgb_from_color(color_1), get_rgb_from_color(color_2))
