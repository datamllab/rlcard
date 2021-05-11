'''
    Project: Gui Gin Rummy
    File name: card_image.py
    Author: William Hale
    Date created: 3/14/2020
'''

import os
from PIL import Image, ImageTk, ImageDraw

image_dir = os.path.abspath(os.path.dirname(__file__))
if not os.path.isdir(os.path.join(image_dir, 'cards_png')):
    print('Downloading images...')
    import time
    import urllib.request
    import sys
    import zipfile
    def reporthook(count, block_size, total_size):
        global start_time
        if count == 0:
            start_time = time.time()
            return
        duration = time.time() - start_time
        progress_size = int(count * block_size)
        speed = int(progress_size / (1024 * duration))
        percent = int(count * block_size * 100 / total_size)
        sys.stdout.write("\r...%d%%, %d KB, %d KB/s, %d seconds passed" %
                        (percent, progress_size / (1024), speed, duration))
        sys.stdout.flush()
    zipurl = 'https://dczha.com/files/rlcard/cards_png.zip'
    filehandle, _ = urllib.request.urlretrieve(zipurl, reporthook=reporthook)

    with zipfile.ZipFile(filehandle,"r") as zip_ref:
        zip_ref.extractall(image_dir)

    print()
    print('Done')

ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']
suits = ['C', 'D', 'H', 'S']


def long_rank_name_for(rank: str) -> str:
    rank_exceptions = {'A': 'ace', 'T': '10', 'J': 'jack', 'Q': 'queen', 'K': 'king'}
    result = rank if rank not in rank_exceptions.keys() else rank_exceptions[rank]
    return result


def long_suit_name_for(suit: str) -> str:
    known_suit_name_by_suit = {'C': 'clubs', 'D': 'diamonds', 'H': 'hearts', 'S': 'spades'}
    result = suit if suit not in known_suit_name_by_suit else known_suit_name_by_suit[suit]
    return result


long_rank_name_by_rank = {(rank, long_rank_name_for(rank)) for rank in ranks}
long_suit_name_by_suit = {(suit, long_suit_name_for(suit)) for suit in suits}


def get_card_filename(rank: str, suit: str) -> str:
    long_rank_name = long_rank_name_for(rank)
    long_suit_name = long_suit_name_for(suit)
    card_file_name = "{}/cards_png/{}_of_{}@2x.png".format(image_dir, long_rank_name, long_suit_name)
    return card_file_name


def get_card_back_image(scale_factor: float):
    card_filename = "{}/cards_png/back.jpg".format(image_dir)
    image = Image.open(card_filename)
    image_width, image_height = image.size
    card_scale_factor = 0.25 * scale_factor * 0.666
    card_image_width = int(image_width * card_scale_factor)
    card_image_height = int(image_height * card_scale_factor)
    image = image.resize((card_image_width, card_image_height), Image.ANTIALIAS)
    return image


class CardImage(ImageTk.PhotoImage):

    def __init__(self, rank: str, suit: str, scale_factor: float):
        self.scale_factor = scale_factor
        self.face_up = True
        card_filename = get_card_filename(rank=rank, suit=suit)
        image = Image.open(card_filename)
        image_width, image_height = image.size
        card_scale_factor = 0.25 * self.scale_factor
        card_image_width = int(image_width * card_scale_factor)
        card_image_height = int(image_height * card_scale_factor)
        image = image.resize((card_image_width, card_image_height), Image.ANTIALIAS)
        super().__init__(image=image, name="{}{}".format(rank, suit))


class CardBackImage(ImageTk.PhotoImage):

    def __init__(self, scale_factor: float):
        self.scale_factor = scale_factor
        card_filename = get_card_filename(rank='A', suit='C')  # want to use AC which has a lot of white space
        image = Image.open(card_filename)
        image_width, image_height = image.size
        card_scale_factor = 0.25 * self.scale_factor
        card_image_width = int(image_width * card_scale_factor)
        card_image_height = int(image_height * card_scale_factor)
        image = image.resize((card_image_width, card_image_height), Image.ANTIALIAS)
        draw = ImageDraw.Draw(image)
        shape = [3 * self.scale_factor,
                 3 * self.scale_factor,
                 card_image_width - 3 * self.scale_factor,
                 card_image_height - 3 * self.scale_factor]
        draw.rectangle(shape, fill='white', outline=None)
        # paste back image
        card_back_image = get_card_back_image(scale_factor=1.08 * self.scale_factor)
        width = card_back_image.width
        height = card_back_image.height
        crop_left = int(10 * self.scale_factor)
        crop_top = int(10 * self.scale_factor)
        crop_right = width - int(10 * self.scale_factor)
        crop_bottom = height - int(10 * self.scale_factor)
        card_back_image = card_back_image.crop((crop_left, crop_top, crop_right, crop_bottom))
        image.paste(card_back_image, (int(6 * self.scale_factor), int(7 * self.scale_factor)))
        super().__init__(image=image, name="cardBackImage")


class BlankCardImage(ImageTk.PhotoImage):  # FIXME: not used

    def __init__(self, rank: str, suit: str, scale_factor: float):
        self.scale_factor = scale_factor
        card_filename = get_card_filename(rank=rank, suit=suit)
        image = Image.open(card_filename)
        image_width, image_height = image.size
        card_scale_factor = 0.25 * self.scale_factor
        card_image_width = int(image_width * card_scale_factor)
        card_image_height = int(image_height * card_scale_factor)
        image = image.resize((card_image_width, card_image_height), Image.ANTIALIAS)
        # image.putalpha(128)

        # draw = ImageDraw.Draw(image)
        # shape = [(3 * self.scale_factor, 3 * self.scale_factor),
        #          (card_image_width - 3 * self.scale_factor, card_image_height - 3 * self.scale_factor)]
        # draw.rectangle(shape, fill="gray", outline=None)
        # image.putalpha(128)
        draw = ImageDraw.Draw(image)
        shape = [(0, 0), (card_image_width, card_image_height)]
        draw.rectangle(shape, fill="black", outline=int(1 * self.scale_factor))
        # image.putalpha(128)

        super().__init__(image=image, name="blankCardImage")


class BorderLessCardImage(ImageTk.PhotoImage):  # FIXME: not used

    def __init__(self, rank: str, suit: str, scale_factor: float):
        self.scale_factor = scale_factor
        card_filename = get_card_filename(rank=rank, suit=suit)
        image = Image.open(card_filename)
        image_width, image_height = image.size
        card_scale_factor = 0.25 * self.scale_factor
        card_image_width = int(image_width * card_scale_factor)
        card_image_height = int(image_height * card_scale_factor)
        image = image.resize((card_image_width, card_image_height), Image.ANTIALIAS)

        draw = ImageDraw.Draw(image)
        shape = [(0, 0), (card_image_width, card_image_height)]
        draw.rectangle(shape, fill="white", outline=int(1 * scale_factor))
        for i in range(4):
            top = 0
            right = 0
            left = card_image_width
            bottom = card_image_height
            shapes = []
            shape_size = 3.5 * scale_factor
            shapes.append((right, top, right + shape_size, top + shape_size))
            shapes.append((left - shape_size - 1 * scale_factor, top, left + shape_size, top + shape_size))
            shapes.append((left - shape_size - 0 * scale_factor, bottom - shape_size, left, bottom))
            shapes.append((right, bottom - shape_size, right + shape_size, bottom))
            ImageDraw.Draw(image).rectangle(shapes[i], fill="white")

        super().__init__(image=image, name="{}{}".format(rank, suit))
