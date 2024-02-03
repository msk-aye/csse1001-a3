import tkinter as tk
from tkinter import Toplevel, messagebox
from PIL import Image, ImageTk
from typing import *
from a2_solution import *
from a2_support import *
from a3_support import *
from constants import *


__author__ = "Muhammad Khan, 47511921"
__email__ = "m.khan2@uqconnect.edu.au"


# Constants
STATS_DIMENSIONS = (2, 4)
STATS_COIN_POSITION = (1, 3)
ITEM_PADDING = 7
CONTROL_FRAME_HEIGHT = 100
BUTTON_PADDING = 5


# Task 1
class LevelView(AbstractGrid):
    """ Class for generating the visualisation of the maze, Containing all
        tiles and items. Inherits from AbstractGrid, which provides basic
        functionality for grids and is a canvas.
    """

    def __init__(self, master: Union[tk.Tk, tk.Frame],
                 dimensions: tuple[int, int],
                 size: tuple[int, int], **kwargs) -> None:
        """ Constructor for AbstractGrid.

        Parameters:
            master: the master frame for this Canvas.
            dimensions: (#rows, #columns)
            size: (width in pixels, height in pixels)
        """
        super().__init__(master, dimensions, size, **kwargs)
        self.pack(side=tk.LEFT)

    def draw(self, tiles: list[list[Tile]], items: dict[tuple[int, int], Item],
             player_pos: tuple[int, int]) -> None:
        """ Method to craete the graphical maze instance.

        Args:
            tiles: list of tiles in the maze, in the format of a list of list
                   of tile ids, where each sublist represents a row.
            items: dictionary of items within the maze, keys are positions and
                   values are instances of item.
            player_pos: current position of the player.
        """
        self.clear()

        for row_num, row in enumerate(tiles):
            for tile_num, tile in enumerate(row):
                # draw tiles
                tile_id = (tile.get_id())
                position = row_num, tile_num

                bbox = self.get_bbox((row_num, row.index(tile)))

                colour = TILE_COLOURS[tile_id]
                self.create_rectangle(bbox, fill=colour)

                # draw items
                if position in items.keys():
                    item_id = items[position].get_id()
                    colour = ENTITY_COLOURS[item_id]

                    self.create_oval(bbox, fill=colour)
                    self.annotate_position(position, item_id)

                # draw player
                if position == player_pos:
                    player = Player(position)
                    colour = ENTITY_COLOURS[player.get_id()]

                    self.create_oval(bbox, fill=colour)
                    self.annotate_position(position, player.get_id())


class StatsView(AbstractGrid):
    """ Class for generating the visualisation of the players' stats (health,
        hunger, thirst, coins). Inherits from AbstractGrid, which provides
        basic functionality for grids and is a canvas.
    """

    def __init__(self, master: Union[tk.Tk, tk.Frame], width: int, **kwargs)\
            -> None:
        """Constructor for the StatsView, stores self variables.

        Parameters:
            master: the master frame for this Canvas.
            width: the pixel width of the StatsView
        """
        super().__init__(master, (STATS_DIMENSIONS), (width, STATS_HEIGHT),
                         **kwargs)
        self.pack(side=tk.BOTTOM, fill=tk.X)

    def draw_stats(self, player_stats: tuple[int, int, int]) -> None:
        """ Method to create the graphical statsview instance.

        Args:
            player_stats: tuple containing health, hunger and thirst of player.
        """
        for row, info in enumerate([["HP", "Hunger", "Thirst", "Coins"],
                                    player_stats]):
            for col, stats in enumerate(info):
                self.annotate_position((row, col), stats)

    def draw_coins(self, num_coins: int) -> None:
        """Helper function to draw coins.

        Args:
            num_coins: number of coins player currently has.
        """
        self.annotate_position((STATS_COIN_POSITION), num_coins)


class InventoryView(tk.Frame):
    """ Class for generating the visualisation of the players' inventory.
        Inherits from tk.Frame, which provides makes it a frame.
    """

    def __init__(self, master: Union[tk.Tk, tk.Frame], **kwargs) -> None:
        super().__init__(master, width=INVENTORY_WIDTH, **kwargs)
        """ Constructor for the InventoryView class. Creates a title label and
            stores variables for later use.
        """
        self.pack(side=tk.RIGHT, fill=tk.Y)
        self._master = master
        self.title = tk.Label(self, text='Inventory', font=HEADING_FONT)
        self.title.pack(side=tk.TOP)

    def set_click_callback(self, callback: Callable[[str], None]) -> None:
        """Setter method to assign a callback function to the items in the
           inventory.

        Args:
            callback: a function that will be bound to the items.
        """
        self.callback = callback

    def clear(self) -> None:
        """ clears current inventory instance by destroying all labels """
        for widget in self.winfo_children():
            if widget != self.title:
                widget.destroy()

    def _draw_item(self, name: str, num: int, colour: str) -> None:
        """ Draws a single item by making a label and setting a bind to it.

        Args:
            name: string name of item.
            num: number of items within that class there are.
            colour: background colour of label, predetermined in constants.py.
        """
        if name != 'Coin':  # method does not draw coins
            item = tk.Label(self, text=f'{name}: {num}', bg=colour)
            item.pack(side=tk.TOP, ipady=ITEM_PADDING, fill=tk.X)

            item.bind('<Button-1>', lambda e: self.callback(name))

    def draw_inventory(self, inventory: Inventory) -> None:
        """ Method to draw all items in inventory by repeatedly calling the
            private _draw_item method for all items.

        Args:
            inventory (Inventory): _description_
        """
        for item in inventory.get_items().keys():
            num = len(inventory.get_items()[item])
            item_id = (inventory.get_items()[item][0]).get_id()
            colour = ENTITY_COLOURS[item_id]
            self._draw_item(item, num, colour)


class GraphicalInterface(UserInterface):
    """ Class for crearing the basic GUI. Instantiates a LevelView, StatsView
        and InventoryView """

    def __init__(self, master: tk.Tk) -> None:
        """ Constructor for the GraphicalInterface. Stores variables and
            creates a title label with text MazeRunner.

        Args:
            master: tk.Tk() root window for the GraphicalInterface
        """
        self._master = master
        self._master.title("MazeRunner")

        self.titlebar = tk.Label(self._master, text="MazeRunner",
                                 font=BANNER_FONT, bg=THEME_COLOUR)
        self.titlebar.pack(fill=tk.X)

        self.level = None
        self.stat = None
        self.inventory = None

    def create_interface(self, dimensions: tuple[int, int]) -> None:
        """ Instanticates the different views. Packs InventoryView and 
            LevelView into seperate frame.

        Args:
            dimensions: maze level dimensions (row, col).
        """
        self.frame = tk.Frame(self._master)
        self.frame.pack(side=tk.TOP)
        self._dimensions = dimensions

        self.level = LevelView(self.frame, dimensions,
                               (MAZE_WIDTH, MAZE_HEIGHT))
        self.stat = StatsView(self._master, (MAZE_WIDTH + INVENTORY_WIDTH),
                              bg=THEME_COLOUR)
        self.inventory = InventoryView(self.frame)

    def clear_all(self) -> None:
        """ Method to clear everything in order to redraw. """
        if self.level is not None:  # meaning nothing is yet instantiated
            self.level.clear()
            self.stat.clear()
            self.inventory.clear()

    def set_maze_dimensions(self, dimensions: tuple[int, int]) -> None:
        """ Method to create a new maze, with new dimensions. Used for
            processing level_up.

        Args:
            dimensions: new dimensionf for maze.
        """
        self.level.destroy()
        self.stat.destroy()
        self.inventory.destroy()
        self.frame.destroy()
        self.create_interface(dimensions)

    def bind_keypress(self, command: Callable[[tk.Event], None]) -> None:
        """ Sets a function to a keypress

        Args:
            command: function to set to keypress.
        """
        self._master.bind('<Key>', command)

    def set_inventory_callback(self, callback: Callable[[str], None]) -> None:
        """ Sets click callback for inventory.

        Args:
            callback: function to be bound to items within inventory.
        """
        self.inventory.set_click_callback(callback)

    def draw_inventory(self, inventory: Inventory) -> None:
        """ Draws the inventory by calling draw method for inventory.

        Args:
            inventory: players inventory instance.
        """
        self.inventory.draw_inventory(inventory)

    def draw(self, maze: 'Maze', items: dict[tuple[int, int], 'Item'],
             player_position: tuple[int, int], inventory: 'Inventory',
             player_stats: tuple[int, int, int]) -> None:
        """ Draws the current game state.

        Parameters:
            maze: The current Maze instance
            items: The items on the maze
            player_position: The position of the player
            inventory: The player's current inventory
            player_stats: The (HP, hunger, thirst) of the player
        """
        self._draw_level(maze, items, player_position)
        self._draw_player_stats(player_stats)
        self._draw_inventory(inventory)

    def _redraw(self) -> None:
        """ Redraws the game state based of current values. """
        self.clear_all()
        self._view.draw(
            self._model.get_current_maze(),
            self._model.get_current_items(),
            self._model.get_player().get_position(),
            self._model.get_player_inventory(),
            self._model.get_player_stats()
        )

    def _draw_inventory(self, inventory: Inventory) -> None:
        """ Draws the inventory instance.

        Args:
            inventory: inventory instance of player.
        """
        self.inventory.clear()
        self.draw_inventory(inventory)
        self.stat.draw_coins(self.get_player_coins(inventory))

    def get_player_coins(self, inventory: Inventory) -> int:
        """ Counts the players coins currently.

        Args:
            inventory: inventory isntance of player.

        Returns:
            int: number of coins
        """
        items = inventory.get_items()
        return len(items.get("Coin", [],))

    def _draw_level(self, maze: Maze, items: dict[tuple[int, int], Item],
                    player_position: tuple[int, int]) -> None:
        """ Draws the level of the game.

        Args:
            maze: maze instance, contians tiles and items.
            items: dictionary containing the position and mapping of items.
            player_position (tuple[int, int]): _description_
        """
        self.level.draw(maze.get_tiles(), items, player_position)

    def _draw_player_stats(self, player_stats: tuple[int, int, int]) -> None:
        """ Draws the player stats.

        Args:
            player_stats: tuple containing health, hunger and thirst of player.
        """
        self.stat.clear()
        self.stat.draw_stats(player_stats)


class GraphicalMazeRunner(MazeRunner):
    """ Controller class for the game. In charge of gameplay and event
        handling. Inherits from MazeRunner (controller class of the text game).
    """

    def __init__(self, game_file: str, root: tk.Tk) -> None:
        """ Constructor for the GraphicalMazeRunenr instance. Saves variables
            and instantiates a GraphicalInterface as the view class. """
        super().__init__(game_file, root)
        self._master = root
        self._player = self._model.get_player()
        self._view = GraphicalInterface(root)

    def _handle_keypress(self, e: tk.Event) -> None:
        """ Handles the keypress event. Ignores all keys apart from 'WASD'.

        Args:
            e: Event that triggers the player movement.
        """
        if e.char in ['w', 'a', 's', 'd']:
            self._handle_move(e.char)

            if self._model.has_won():
                mbox = messagebox.showinfo(
                    title="You Win",
                    message=WIN_MESSAGE)
                self._master.destroy()
                return

            if self._model.has_lost():
                mbox = messagebox.showinfo(
                    title="You Lost", message=LOSS_MESSAGE)
                self._master.destroy()
                return

            if self._model.did_level_up():
                self._view.set_maze_dimensions(
                    self._model.get_current_maze().get_dimensions())

            self._redraw()
            self._view.set_inventory_callback(self._apply_item)

    def _apply_item(self, item_name: str) -> None:
        """ Method to implement the use of an item and then remove it from
            inventory.

        Args:
            item_name: name of the item.
        """
        pos = (1, 1)  # arbitrary position for instantiating items

        # checks if the item name is in the set of applyable items
        for item in [Potion(pos), Water(pos), Honey(pos), Apple(pos)]:
            if (item.get_name()).lower() == item_name.lower():
                item.apply(self._player)
                self._player.get_inventory().remove_item(item_name)

        self._redraw()
        self._view.set_inventory_callback(self._apply_item)

    def play(self) -> None:
        """ Method to handle the gameplay."""
        self._view.clear_all()
        self._view.create_interface(self._model.get_level().get_dimensions())
        self._view.set_inventory_callback(self._apply_item)
        self._view.bind_keypress(self._handle_keypress)

        self._view.draw(self._model.get_current_maze(),
                        self._model.get_current_items(),
                        self._model.get_level().get_player_start(),
                        self._model.get_player_inventory(),
                        (self._model.get_player_stats()))


# Task 2
class ImageLevelView(LevelView):
    """ LevelView class to account for images, inherits from LevelView"""

    def draw(self, tiles: list[list[Tile]], items: dict[tuple[int, int], Item],
             player_pos: tuple[int, int]) -> None:
        """ Draws the level with the correct image representation of each tile.

        Args:
            tiles: list of tiles in the maze.
            items: dictionary of item postions and mappings in the maze.
            player_pos: player position (row, col).
        """
        self.clear()

        # loads all images into dictionary and resizes them
        self.images = {
            WALL: ImageTk.PhotoImage(Image.open("images/wall.png")\
                .resize(self.get_cell_size())),
            EMPTY: ImageTk.PhotoImage(Image.open('images/grass.png')\
                .resize(self.get_cell_size())),
            LAVA: ImageTk.PhotoImage(Image.open('images/lava.png')\
                .resize(self.get_cell_size())),
            DOOR: ImageTk.PhotoImage(Image.open('images/door.png')\
                .resize(self.get_cell_size())),
            COIN: ImageTk.PhotoImage(Image.open('images/coin.png')\
                .resize(self.get_cell_size())),
            POTION: ImageTk.PhotoImage(Image.open('images/potion.png')\
                .resize(self.get_cell_size())),
            HONEY: ImageTk.PhotoImage(Image.open('images/honey.png')\
                .resize(self.get_cell_size())),
            APPLE: ImageTk.PhotoImage(Image.open('images/apple.png')\
                .resize(self.get_cell_size())),
            WATER: ImageTk.PhotoImage(Image.open('images/water.png')\
                .resize(self.get_cell_size())),
            PLAYER: ImageTk.PhotoImage(Image.open('images/player.png')\
                .resize(self.get_cell_size())),
        }

        for row_num, row in enumerate(tiles):
            for tile_num, tile in enumerate(row):
                tile_id = (tile.get_id())
                position = (row_num, tile_num)
                position_cords = self.get_midpoint(position)

                self.create_image(position_cords, image=self.images[tile_id])

                if position in items.keys():
                    item_id = items[position].get_id()

                    self.create_image(
                        position_cords, image=self.images[item_id])

                if position == player_pos:
                    player = Player(position)

                    self.create_image(
                        position_cords, image=self.images[player.get_id()])


class ControlsFrame(tk.Frame):
    """ Class that creates a controller frame on the bottom of the window. """
    def __init__(self, master: Union[tk.Tk, tk.Frame], 
                 controller: GraphicalMazeRunner, **kwargs) -> None:
        """ Constructor for controls frame. Instantiates frame and buttons.

        Args:
            master : root window.
            controller: the GraphicalMazeRunner (game) instance.
        """
        super().__init__(master, height=CONTROL_FRAME_HEIGHT, **kwargs)
        self.pack(side=tk.BOTTOM, fill=tk.X)
        self._master = master

        restart = tk.Button(self, text="Restart game",
                            command=controller.restart_game)
        restart.pack(side=tk.LEFT, expand=tk.TRUE, ipadx=BUTTON_PADDING)

        new_game = tk.Button(self, text="New game",
                             command=controller.new_game)
        new_game.pack(side=tk.LEFT, expand=tk.TRUE, ipadx=BUTTON_PADDING)

        frame = tk.Frame(self)
        frame.pack(side=tk.LEFT, expand=tk.TRUE)

        title = tk.Label(frame, text='Timer')
        title.pack(side=tk.TOP, expand=tk.TRUE)

        self.mins = 0
        self.secs = 0

        self.timer = tk.Label(frame, text=f'{self.mins}m {self.secs}s')
        self.timer.pack(side=tk.BOTTOM, expand=tk.TRUE)

        self._master.after(1000, self.increment_timer)

    def increment_timer(self) -> None:
        """ Method to create add functionality of a timer. """
        if self.secs <= 59:
            self.secs += 1

        if self.secs == 60:
            self.secs = 0
            self.mins += 1

        self.timer.config(text=f'{self.mins}m {self.secs}s')
        self._master.after(1000, self.increment_timer)


class ImageGraphicalInterface(GraphicalInterface):
    """ Graphical Interface but to accoutn for the images. Does same thing
        as parent class except it calls ImageLevelView. """
    def create_interface(self, dimensions: tuple[int, int]) -> None:
        """ Creates the interface with ImageLevelView.

        Args:
            dimensions: dimension of maze (#rows, #colums)
        """
        super().create_interface(dimensions)
        self.level.destroy()
        self.level = ImageLevelView(self.frame, dimensions,
                                    (MAZE_WIDTH, MAZE_HEIGHT))


class ImageGraphicalMazeRunner(GraphicalMazeRunner):
    """ GraphicalMazeRunner in order to account for images. """
    def __init__(self, game_file: str, root: tk.Tk) -> None:
        """ Constructor for ImageGraphicalMazeRunner. Saves variables,
            instantiates controls frame and view.

        Args:
            game_file: game to be played.
            root: window to pack in.
        """
        super().__init__(game_file, root)
        self._view.titlebar.destroy()
        del self._view
        self._view = ImageGraphicalInterface(root)
        self._controls_frame = ControlsFrame(self._master, self)

    def restart_game(self) -> None:
        """ Functionality for the restart option on file menu and the restart
            button in controls frame. Destroys all widges and creates an new
            game.
        """
        for widget in self._master.winfo_children():
            widget.destroy()

        play_game(self._master)

    def new_game(self) -> None:
        """ Functionality for New Game button in controller frame. Asks for a
            game file and then attempts to open the game. If the file is not
            valid reurns none.
        """
        self.window = Toplevel()
        self.window.title("Enter New Game File")
        self.window.geometry("300x40")

        self.new_game_prompt = tk.Entry(self.window)
        self.new_game_prompt.pack(side=tk.LEFT, expand=tk.TRUE, fill=tk.X)

        Enter = tk.Button(self.window, text='Enter',
                          command=self.new_game_file)
        Enter.pack(side=tk.RIGHT, padx=15)

    def new_game_file(self) -> None:
        """ Command function for the enter button. Attempts to run game. """
        game_file = self.new_game_prompt.get()
        global GAME_FILE
        GAME_FILE = f'{game_file}'

        try:
            ImageGraphicalMazeRunner(GAME_FILE, self._master)
            self.restart_game()

        except:
            mbox = messagebox.showinfo(
                title="Game file not valid",
                message="Game file not valid")
            self.window.destroy()

    def quit_game(self) -> None:
        """ Method to terminate the window after confirmation. """
        mbox = messagebox.askyesno(
            title="Quit?",
            message="Do you want to quit?")
        if mbox:
            self._master.destroy()

    def save_game(self) -> None:
        """ Method to save the progress of the game. """
        pass
    
    def load_game(self) -> None:
        """ Method to load a saved game. """
        pass

    def play(self) -> None:
        """ Play method. Handles gameplay. """
        self._view.clear_all()
        self._view.create_interface(self._model.get_level().get_dimensions())
        self._view.set_inventory_callback(self._apply_item)
        self._view.bind_keypress(self._handle_keypress)

        self._view.draw(self._model.get_current_maze(),
                        self._model.get_current_items(),
                        self._model.get_level().get_player_start(),
                        self._model.get_player_inventory(),
                        (self._model.get_player_stats()))


# Main execution functions
def play_game(root: tk.Tk):
    """ Function to play game by creating an instance of GraphicalMazeRunner

    Args:
        root: window tha game is in.
    """
    if TASK == 1:
        game = GraphicalMazeRunner(GAME_FILE, root)

    if TASK == 2:
        game = ImageGraphicalMazeRunner(GAME_FILE, root)

        # creation of menu
        menu = tk.Menu(root)

        file_menu = tk.Menu(menu)
        menu.add_cascade(label="File", menu=file_menu)

        file_menu.add_command(label="Save game", command=game.save_game)
        file_menu.add_command(label="Load game", command=game.load_game)
        file_menu.add_command(label="Restart game", command=game.restart_game)
        file_menu.add_command(label="Quit", command=game.quit_game)

        root.config(menu=menu)

    game.play()
    root.mainloop()


# Creation of window
def main():
    """ Executes gameplay."""
    root = tk.Tk()
    play_game(root)


if __name__ == '__main__':
    main()
