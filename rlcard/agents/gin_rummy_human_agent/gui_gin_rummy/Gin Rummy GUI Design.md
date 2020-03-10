#Gin Rummy GUI Design

## Acknowledgment
The Gin Rummy app is a major refactoring of the code for a chess program by Bhaskar Chaudhary.
The chess program is explained in the video course "Tkinter GUI Application Development Projects".
You can do a google search on "Bhaskar Chaudhary tkinter packt" for more information.
The code for the chess program is available at https://github.com/PacktPublishing/Tkinter-GUI-Application-Development-Projects.

## Window Size Factor

## Scale Factor

## Card_id
You can control how a card_id is assigned to a card image.
For example, you may want the cards to be in your preferred order when you sort by card_id.
The ranks and suits have an order specified by the following code:
```python
    rank_names = ['ace', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'jack', 'queen', 'king']
    suit_name = ['clubs', 'diamonds', 'hearts', 'spades']
```
To control the card_id assigned to a card image, you need to define a method get_rank_suit_ids.
For example:
```python
def get_gin_rummy_rank_suit_ids(card_id: int) -> (int, int):
    rank_id = card_id // 4
    suit_id = card_id % 4
    return rank_id, suit_id
```
This will arrange the cards by rank from ace to king, by suit from clubs to spades.

You create the card_images as follows:
```python
self.card_images = []
self.card_item_ids = []
for card_id in range(52):
    card_image = CardImage(card_id=card_id,
                           scale_factor=self.scale_factor,
                           get_rank_suit_ids=utils.get_gin_rummy_rank_suit_ids)
    self.card_images.append(card_image)
    card_item_id = self.create_image((0, -9999), image=card_image, anchor="nw")
    self.card_item_ids.append(card_item_id)
    self.itemconfigure(card_item_id, state=tk.HIDDEN)
```
The card_item_ids are initially hidden and put off screen. They will not be visible initially.

If you know the card_id, then you can get its card_item_id by:
```python
card_item_id = self.card_item_ids[card_id]
```

You can get the rank_id and suit_id from the card_id by:
```python
rank_id, suit_id = utils.get_gin_rummy_rank_suit_ids(card_id=card_id)
```

## Box Item (e.g. discard_pile_box_item)
Some users like an area to be displayed if it is empty.
For example, a card game may have a discard pile which can be empty at times.
You can create a rectangle item of the same size of a card and put it where the cards will be discarded.
When a player discards a card, the box will be covered and no longer visible.
For example:

```python
    # draw discard_pile_box_item
    discard_pile_box_left = self.discard_pile_anchor[0]
    discard_pile_box_top = self.discard_pile_anchor[1]
    discard_pile_box_right = discard_pile_box_left + card_width
    discard_pile_box_bottom = discard_pile_box_top + card_height
    self.discard_pile_box_item = self.create_rectangle(discard_pile_box_left,
                                                        discard_pile_box_top,
                                                        discard_pile_box_right,
                                                        discard_pile_box_bottom,
                                                        fill="gray")
```
If a 'show discard pile outline' user preference is false, you can set the fill to be an empty string.

## GUIEvent

## To Do
* Implement drag-and-drop for cards.
* Increase white margin space for face of cards.
* Implement reverse fan of a card pile.
* Don't rely on the assumption that the card_item_ids are in sorted order when arranging held cards.
* Implement highlighting to select cards rather than jogging them.
* Provide preference to show/hide discard_pile_box.
* Find a cross platform method to play a beep sound.
* Add alerts for warning errors.
* Add alerts for program logic errors.

## Gin Rummy game

* Number of players: 2
* 52 cards, from ace low to king high
* Names of players: North, South
* First mover: non-dealer (the opponent is called the dealer)

### Legal actions
1) draw_from_stock_pile
1) pick_up_card_from_discard_pile
1) declare_dead_hand (terminal action)
1) discard card
1) knock card (terminal action)

### Scoring method
ToDo: ???????
