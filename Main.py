import Game
import Player
from PokerGUI import PokerGUI
import tkinter as tk 

if __name__ == "__main__":
    #game = Game.Game()
    #game.main()
    root = tk.Tk()
    gui = PokerGUI(root)
    root.mainloop()