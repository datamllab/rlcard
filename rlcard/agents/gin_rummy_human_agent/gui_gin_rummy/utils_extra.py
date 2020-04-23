'''
    Project: Gui Gin Rummy
    File name: utils_extra.py
    Author: William Hale
    Date created: 3/14/2020
'''

from PIL import Image, ImageDraw, ImageFilter


def rounded_rectangle(self: ImageDraw, xy, corner_radius, fill=None, outline=None):  # FIXME: not used
    upper_left_point = xy[0]
    bottom_right_point = xy[1]
    self.rectangle(
        [
            (upper_left_point[0], upper_left_point[1] + corner_radius),
            (bottom_right_point[0], bottom_right_point[1] - corner_radius)
        ],
        fill=fill,
        outline=outline
    )
    self.rectangle(
        [
            (upper_left_point[0] + corner_radius, upper_left_point[1]),
            (bottom_right_point[0] - corner_radius, bottom_right_point[1])
        ],
        fill=fill,
        outline=outline
    )
    self.pieslice(
        [upper_left_point, (upper_left_point[0] + corner_radius * 2, upper_left_point[1] + corner_radius * 2)],
        180,
        270,
        fill=fill,
        outline=outline
        )
    self.pieslice(
        [(bottom_right_point[0] - corner_radius * 2, bottom_right_point[1] - corner_radius * 2), bottom_right_point],
        0,
        90,
        fill=fill,
        outline=outline
        )
    self.pieslice([(upper_left_point[0], bottom_right_point[1] - corner_radius * 2),
                   (upper_left_point[0] + corner_radius * 2, bottom_right_point[1])],
                  90,
                  180,
                  fill=fill,
                  outline=outline
                  )
    self.pieslice([(bottom_right_point[0] - corner_radius * 2, upper_left_point[1]),
                   (bottom_right_point[0], upper_left_point[1] + corner_radius * 2)],
                  270,
                  360,
                  fill=fill,
                  outline=outline
                  )


ImageDraw.rounded_rectangle = rounded_rectangle  # FIXME: not used


def mask_rounded_rectangle_transparent(pil_img, corner_radius=8):  # FIXME: not used
    blur_radius = 0  # FIXME: what is this for ??? wch
    mask = Image.new("L", pil_img.size, 0)
    draw = ImageDraw.Draw(mask)
    rounded_rectangle(draw, xy=((0, 0), (pil_img.size[0], pil_img.size[1])), corner_radius=corner_radius, fill=255)

    mask = mask.filter(ImageFilter.GaussianBlur(blur_radius))
    result = pil_img.copy()
    result.putalpha(mask)
    return result
