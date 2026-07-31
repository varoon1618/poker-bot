import tkinter as tk
from GameEngine import PokerEngine
from UI import PokerGUI

if __name__ == "__main__":
  root = tk.Tk()
  poker_engine = PokerEngine()
  gui = PokerGUI(root, engine=poker_engine)
  poker_engine.register_listener(gui.update_display)
  poker_engine.initialise_game()
  root.mainloop()