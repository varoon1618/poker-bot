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
    game.communityCards = ['d3','c4','h8','h3','h10']
    player = Player.Player()
    player.init(1,"varun",500,"human")
    player.hand = ['c9','d8']
    s1 = game.scoreHand(player)
    print(s1)
  