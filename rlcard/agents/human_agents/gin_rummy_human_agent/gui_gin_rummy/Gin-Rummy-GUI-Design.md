#Gin Rummy GUI Design

## Acknowledgment
The Gin Rummy app is a major refactoring of the code for a chess program by Bhaskar Chaudhary.
The chess program is explained in the video course "Tkinter GUI Application Development Projects".
You can do a google search on "Bhaskar Chaudhary tkinter packt" for more information.
The code for the chess program is available at <https://github.com/PacktPublishing/Tkinter-GUI-Application-Development-Projects>.

## Requirements
You need to install tkinter if it is not already installed.
Tkinter is Python's defacto standard GUI (Graphical User Interface) package.
It is a thin object-oriented layer on top of Tcl/Tk.
Note that the name of the module is ‘tkinter’.

If you are using anaconda:
* I have version 8.6.11 to work with version 3.6 of Python.
* In the installed window for your environment, search for "tk".
* If it is found, make sure you have at least version 8.6.11.
* Otherwise, go to the "Not installed" window, search for "tk", select it, and apply it.

If you are using Ubuntu:
* You can install it with apt-get install python-tk.

For other cases, you can search on google to see how to install tkinter.

## GameFrame
The GameFrame class uses the following parameters:

*   window_title: str
*   base_height: int
*   base_width: int
*   scale_factor_multiplier: float

The base_height and base_width only determine the aspect ratio for the frame size.
The actual size of the window is calculated from these values and the 'window size factor' preference.
The window size will vary from 50% to 100% of the total screen size.

The scale_factor_multiplier determines the size of the cards.
Start will a value of 1.0 and adjust up or down.
The program uses a value of 1.5 for the scale_factor_multiplier.

The window is centered in the screen.
Its origin is determined by the following;

*   window_x: int
*   window_y: int

A new game is started when the GameFrame is initialized.

## GameCanvas
The GameCanvas class specifies and layouts the widgets and canvas items for the game.

The GameFrame provides the initializer of the GameCanvas with the following value:

*   scale_factor: float

The GameCanvas needs to scale the layout values of its widgets by multiplying by this value.
For example, for a margin of 10, it would use 10 times scale_factor.
It also calculate the scaled card size and uses the width and height of a card to do layout.
For example, it specifies that the discard pile x origin to be card_width times 1.5
away from the stock pile x origin.
It does not need to worry about the scale_factor in this case since it is built into the card_width.

The GameCanvas has access to its canvas items only by their integer item_id.
Thus, it needs to keep track of the canvas_items that it creates.
```python
    # keep list of relevant canvas items
    canvas_items = []  # type: [CanvasItem]
```
When all the canvas_items have been recorded, it will create the association of canvas_item by item_id as follows:
```python
    # dictionary of item_id to canvas_item with that item_id
    canvas_item_by_item_id = {}
    for canvas_item in canvas_items:
        canvas_item_by_item_id[canvas_item.item_id] = canvas_item
```

The GameCanvas creates the card images as follows:
```python
    # Make card images
    card_back_image = CardBackImage(scale_factor=scale_factor)
    card_images = {}  # type: Dict[(str, str)]
    for card_id in range(52):
        card = gin_rummy_utils.card_from_card_id(card_id)
        card_image = CardImage(rank=card.rank, suit=card.suit, scale_factor=scale_factor)
        card_images[card.rank, card.suit] = card_image
```
It needs to save each card_image in card_images otherwise they will be released.

The GameCanvas creates the canvas card image items as follows:

```python
    # Make card_item_ids by card_id
    card_item_ids = []  # type: List[int]
    for card_id in range(52):
        card = gin_rummy_utils.card_from_card_id(card_id)
        card_image = card_images[card.rank, card.suit]
        card_item_id = self.create_image((0, -9999), image=card_image, anchor="nw")
        self.itemconfigure(card_item_id, state=tk.HIDDEN)
        card_item_ids.append(card_item_id)
```

It uses the card_image to create an image item on the canvas.
The canvas image items are hidden and placed off screen.

The GameCanvas has access to the canvas card image item only by its card_item_id.
It is useful to have some way to get the card (its rank and its suit) from the card_item_id.
For each card_item_id, it creates a CardItem and records it into the canvas_items.
The card_items array is a way to access the card_item by its card_id.
```python
    # Make card_items by card_id
    card_items = []  # type: List[CardItem]
    for card_id in range(52):
        card = gin_rummy_utils.card_from_card_id(card_id)
        card_item_id = card_item_ids[card_id]
        card_image = card_images[card.rank, card.suit]
        card_item = CardItem(item_id=card_item_id, card_id=card_id, card_image=card_image, game_canvas=self)
        card_items.append(card_item)
        canvas_items.append(card_item)
```

The GameCanvas uses the card width and card height in some of its layout calculations.
It get these values as follows:
```python
    # Get card dimension
    card_width = card_images["A", "S"].width()
    card_height = card_images["A", "S"].height()
```

### Box Item (e.g. discard_pile_box_item_id)
Some users like an area to be displayed if it is empty.
For example, Gin Rummy has a discard pile which can be empty at times.
The GameCanvas creates a rectangle item of the same size of a card and put it where the cards will be discarded.
When a player discards a card, the box will be covered and no longer visible.
It creates this canvas item as follows:

```python
    # draw discard_pile_box
    discard_pile_box_left = discard_pile_anchor[0]
    discard_pile_box_top = discard_pile_anchor[1]
    discard_pile_box_right = discard_pile_box_left + card_width
    discard_pile_box_bottom = discard_pile_box_top + card_height
    discard_pile_box_item_id = self.create_rectangle(discard_pile_box_left,
                                                     discard_pile_box_top,
                                                     discard_pile_box_right,
                                                     discard_pile_box_bottom,
                                                     fill="gray")
    discard_pile_box_item = CanvasItem(item_id=discard_pile_box_item_id, game_canvas=self)
    canvas_items.append(discard_pile_box_item)
```

### Ghost cards
The cards held by a player can be rearranged.
The target or drop site is specified by the card that will be the insertion point.
However, if the player wants to put some cards at the front of his hand, there is no card to act as the insertion point.
To treat this special case in the same way as the normal case,
the GameCanvas creates invisible "ghost" cards located in front of the first card of the held_pile.
I'm not sure if this is any better than handling it as a special case.
```python
    # create two held_pile ghost card items
    held_pile_ghost_card_items = []
    player_held_pile_anchors = [north_held_pile_anchor, south_held_pile_anchor]
    held_pile_tags = [configurations.NORTH_HELD_PILE_TAG, configurations.SOUTH_HELD_PILE_TAG]
    for player_id in range(2):
        x, y = player_held_pile_anchors[player_id]
        x -= held_pile_tab
        ghost_card_item_id = self.create_rectangle(x, y, x + card_width, y + card_height, width=0, fill='')
        self.itemconfig(ghost_card_item_id, tag=held_pile_tags[player_id])
        ghost_card_item = CanvasItem(item_id=ghost_card_item_id, game_canvas=self)
        canvas_items.append(ghost_card_item)
        held_pile_ghost_card_items.append(ghost_card_item)
```

## Gin Rummy Human Example
The file gin_rummy_human.py is an example of running the Gui Gin Rummy app.
The code is:
```python
# Play game
gin_rummy_app = GameApp(make_gin_rummy_env=make_gin_rummy_env)
```
The method make_gin_rummy_env should be supplied.
The example uses the following:
```python
def make_gin_rummy_env() -> 'GinRummyEnv':
    gin_rummy_env = rlcard.make('gin-rummy')
    # north_agent = RandomAgent(num_actions=gin_rummy_env.num_actions)
    north_agent = GinRummyNoviceRuleAgent()
    south_agent = HumanAgent(gin_rummy_env.num_actions)
    gin_rummy_env.set_agents([north_agent, south_agent])
    return gin_rummy_env
```
You make the gin_rummy_env.
You create a north agent of your choice.
The south agent should be the HumanAgent.
You set the agents for gin_rummy_env.
You can change the configuration of the gin_rummy_env.
You can change the settings of the GinRummyGame.

## GameApp
The GameApp creates the GameFrame and MenuBar.
It starts the mainloop which is the main thread for the gui.
The code is:
```python
class GameApp(object):

    def __init__(self, make_gin_rummy_env: Callable[[], 'GinRummyEnv'] = None):
        self.make_gin_rummy_env = make_gin_rummy_env if make_gin_rummy_env else GameApp._make_gin_rummy_env
        root = tk.Tk()
        root.resizable(False, False)
        self.game_frame = GameFrame(root=root, game_app=self)
        self.menu_bar = MenuBar(root, game_frame=self.game_frame)
        root.mainloop()
```

## EnvThread
The EnvThread is a background daemon thread that runs gin_rummy_env.
It also starts the GameCanvasUpdater loop on the main thread.
It maintains the following variables:
```python
    self.gin_rummy_env = gin_rummy_env
    self.game_canvas = game_canvas
    self.mark = 0
    self.is_stopped = False
```
The mark variable is the number of actions that the GameCanvas has processed.
As the gin_rummy_env processes actions, the GameCanvasUpdater will be notified when a human action is needed.
There may be multiple actions by the non-human opponent that have not been processed by the GameCanvasUpdater.
If the mark variable is less than the number of moves in the move_sheet of the round,
then the GameCanvasUpdater must process these new moves and catch up with gin_rummy_env.
Once it is caught up, it can let the human make an action which will be returned to the gin_rummy-env.

If the human starts a new game via the menu before the current game is completed,
then the variable is_stopped is set to True and the EnvThread does what is necessary to wind down.

## Gin Rummy Human Agent
The HumanAgent supplies the step action when the gin_rummy_env asks for it.
It goes into a wait loop until the GameCanvasUpdater provides the step action taken by the human player.
It maintains the following variables:
```python
    self.is_choosing_action_id = False
    self.chosen_action_id = None  # type: int or None
    self.state = None
```
The HumanAgent sets the state variable to the current state
and sets the variable is_choosing_action_id to be True
when the gin_rummy_env asks for a human step action.
The GameCanvasUpdater monitors the variable is_choosing_action_id,
allows the human player to make a step action when it becomes True,
and sets chosen_action_id to the step action made by the human player.
The HumanAgent ends its wait loop when the chosen_action_id is set and returns it to the gin_rummy_env.

## GameCanvasUpdater
The GameCanvasUpdater runs a loop on the main thread to keep the gui in sync with the gin_rummy_env.
It also returns the action taken by the human player to the gin_rummy_env via the human_agent.
It maintains the following variables:
```python
    self.game_canvas = game_canvas
    self.env_thread = None
    self.pending_human_action_ids = []  # type: List[int]
    self.busy_body_id = None  # type: int or None
    self.is_stopped = False
```
The game_canvas is set on initialization and is never changed.
When a new game starts, the env_thread is set to the new env_thread for the new game
and the last three variables above are reset to their initial values.

The variable pending_human_action_ids is used because the human player can take back certain actions.
For example, if the human player taps the top card of the discard pile to do the pick_up_discard_action,
then he can tap it a second time to cancel that action.

The GameCanvasUpdater runs the following loop on the main thread:
```python
    def apply_canvas_updates(self):
        if not self.env_thread.is_stopped:
            self._advance_mark()
            delay_ms = 1
            self.game_canvas.after(delay_ms, func=self.apply_canvas_updates)
        else:
            self.is_stopped = True
```
It is always trying to advance the mark to keep up with the gin_rummy_env that is running in the env_thread.
The busy_body_id is the player_id whose action is being processed.
There may be a block of non-human actions that it needs to process before it lets the human player take an action.
The human action_ids are placed in pending_human_actions_ids to be returned to the human_agent.

If the human starts a new game via the menu before the current game is completed,
then the variable is_stopped is set to True and the apply_canvas_updates loop terminates.

## starting_new_game
The main code to start a new game is the following:
```python
def start_new_game(game_canvas: 'GameCanvas'):
    if game_canvas.game_canvas_updater.env_thread and game_canvas.game_canvas_updater.env_thread.is_alive():
        game_canvas.game_canvas_updater.env_thread.stop()
        while game_canvas.game_canvas_updater.env_thread.is_alive() or not game_canvas.game_canvas_updater.is_stopped:
            game_canvas.update()  # yield time to other threads and to main thread
    _reset_game_canvas(game_canvas=game_canvas)
    # make new gin_rummy_env
    gin_rummy_env = game_canvas.game_app.make_gin_rummy_env()
    gin_rummy_env.game.settings.going_out_deadwood_count = configurations.GOING_OUT_DEADWOOD_COUNT  # Note this
    gin_rummy_env.game.settings.max_drawn_card_count = configurations.MAX_DRAWN_CARD_COUNT  # Note this
    # start thread
    game_canvas.game_canvas_updater.env_thread = EnvThread(gin_rummy_env=gin_rummy_env, game_canvas=game_canvas)
    game_canvas.game_canvas_updater.env_thread.start()  # Note this: start env background thread
```
If a new game is started via the menu before the current game is completed,
then the env_thread of the current game and the game_canvas_updater loop need to be shut down gracefully.

The game_canvas is reset.

A new gin_rummy_env is created.

A new env_thread is created and started.

## To Do
*   Implement drag-and-drop for cards.
*   Increase white margin space for face of cards.
*   Implement reverse fan of a card pile.
*   Implement highlighting to select cards rather than jogging them.
*   Provide preference to show/hide discard_pile_box.
*   Find a cross platform method to play a beep sound.
*   Add alerts for warning errors.
*   Add alerts for program logic errors.
*   Provide "Help" document in "Help" menu.
