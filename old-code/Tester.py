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
    '''
    bot1 has hand:  d11 h2
varun has hand:  h10 s5
community cards:  h11 d8 s12 d9 h4
    '''
    game.communityCards = ['h11','d8', 's12', 'd9', 'h4']
    player = Player.Player()
    player.init(1,"varun",500,"human")
    player.hand = ['h10','s5']
    s1 = game.scoreHand(player)
    print(s1)
  