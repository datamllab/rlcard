#
#   Gin Rummy
#

from PIL import Image, ImageTk, ImageDraw

image_dir = "../rlcard/agents/gin_rummy_human_agent/gui_cards"

ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']
suits = ['C', 'D', 'H', 'S']


def long_rank_name_for(rank: str) -> str:
    rank_exceptions = {'A': 'ace', 'T': '10', 'J': 'jack', 'Q': 'queen', 'K': 'king'}
    result = f"{rank}" if rank not in rank_exceptions.keys() else rank_exceptions[rank]
    return result


def long_suit_name_for(suit: str) -> str:
    known_suit_name_by_suit = {'C': 'clubs', 'D': 'diamonds', 'H': 'hearts', 'S': 'spades'}
    result = f"{suit}" if suit not in known_suit_name_by_suit else known_suit_name_by_suit[suit]
    return result


long_rank_name_by_rank = {(rank, long_rank_name_for(rank)) for rank in ranks}
long_suit_name_by_suit = {(suit, long_suit_name_for(suit)) for suit in suits}


def get_card_filename(rank: str, suit: str) -> str:
    long_rank_name = long_rank_name_for(rank)
    long_suit_name = long_suit_name_for(suit)
    card_file_name = f"{image_dir}/cards_png/{long_rank_name}_of_{long_suit_name}@2x.png"
    return card_file_name


def get_card_back_image(scale_factor: float):
    card_filename = f"{image_dir}/back@2x.png"
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
        super().__init__(image=image, name=f"{rank}{suit}")


class BetterCardBackImage(ImageTk.PhotoImage):

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
        draw.rectangle(shape, fill="white", width=int(1 * self.scale_factor))
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
        super().__init__(image=image, name="blankCardImage")


class CardBackImage(ImageTk.PhotoImage):  # FIXME: not used

    def __init__(self, scale_factor: float):
        self.scale_factor = scale_factor
        card_back_image = get_card_back_image(scale_factor=scale_factor)
        super().__init__(image=card_back_image, name=f"cardBack")


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
        # draw.rectangle(shape, fill="gray", width=int(1 * self.scale_factor))
        # image.putalpha(128)
        draw = ImageDraw.Draw(image)
        shape = [(0, 0), (card_image_width, card_image_height)]
        draw.rectangle(shape, fill="black", width=int(1 * self.scale_factor))
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
        draw.rectangle(shape, outline="white", width=int(1 * scale_factor))
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

        super().__init__(image=image, name=f"{rank}{suit}")
