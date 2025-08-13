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
    #bot1 has hand:  d10 h7
    #varun has hand:  c2 h4
    #community cards:  s10 s13 h3 d13 s7
    game.communityCards = ['s10','s13', 'h3', 'd13', 's7']
    player = Player.Player()
    player.init(1,"varun",500,"human")
    player.hand = ['d10','h7']
    s1 = game.scoreHand(player)
    print(s1)
  