import Game
import Player
from PokerGUI import PokerGUI
import tkinter as tk 
import queue

if __name__ == "__main__":
    root = tk.Tk()
    action_queue = queue.Queue()
    gui = PokerGUI(root,action_queue)
    game = Game.Game(gui,action_queue)
    root.after(100, game.playGame())
    root.mainloop()
