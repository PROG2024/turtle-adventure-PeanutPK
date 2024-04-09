"""
The main module, responsible for creating a root window containing the game's
main component.
"""
from typing import Final
import tkinter as tk
from turtle_adventure import TurtleAdventureGame

SCREEN_WIDTH: Final = 800
SCREEN_HEIGHT: Final = 500

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Turtle's Adventure")
    root.attributes('-topmost', True)
    root.geometry(f"{SCREEN_WIDTH}x{SCREEN_HEIGHT}")
    root.resizable(False, False)  # games usually have fixed window size
    # Please don't play after lvl 10
    game = TurtleAdventureGame(root, SCREEN_WIDTH, SCREEN_HEIGHT, level=10)
    game.start()
    root.mainloop()
