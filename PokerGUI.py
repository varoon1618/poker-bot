import customtkinter as ctk
from tkinter import messagebox

class PokerGUI:
    def __init__(self, master,action_queue):
      self.action_queue = action_queue
      self.master = master
      master.title("Poker Game")
      master.state('zoomed')        
    
      self.title_label = ctk.CTkLabel(self.master, text="Poker Game", font=("Arial", 24))
      self.title_label.pack(pady=10)

      self.status_label = ctk.CTkLabel(self.master, text="Welcome to Poker!", text_color="blue")
      self.status_label.pack(pady=10)
      
      self.move_label = ctk.CTkLabel(self.master)#label to display player/bot moves
      self.move_label.pack(pady=10)
      
      self.previousBet_label = ctk.CTkLabel(self.master)
      self.previousBet_label.pack(pady=10)
      
      self.player_frame = ctk.CTkFrame(self.master)
      self.player_frame.pack(pady=10)

      self.player_hand_label = ctk.CTkLabel(self.player_frame, text="Your Hand:")
      self.player_hand_label.grid(row=0, column=0, padx=5)
      self.player_hand_cards = ctk.CTkLabel(self.player_frame, text="?")
      self.player_hand_cards.grid(row=0, column=1, padx=5)

      self.community_frame = ctk.CTkFrame(self.master)
      self.community_frame.pack(pady=10)
      self.community_label = ctk.CTkLabel(self.community_frame, text="Community Cards:")
      self.community_label.grid(row=0, column=0, padx=5)
      self.community_cards = ctk.CTkLabel(self.community_frame, text="?")
      self.community_cards.grid(row=0, column=1, padx=5)

      self.pot_label = ctk.CTkLabel(self.master, text="Pot: $0")
      self.pot_label.pack(pady=5)

      self.action_frame = ctk.CTkFrame(self.master)
      self.action_frame.pack(pady=20)
      self.fold_button = ctk.CTkButton(self.action_frame, text="Fold", command=self.fold)
      self.fold_button.grid(row=0, column=0, padx=10)
      self.call_button = ctk.CTkButton(self.action_frame, text="Call", command=self.call)
      self.call_button.grid(row=0, column=1, padx=10)
      self.raise_button = ctk.CTkButton(self.action_frame, text="Raise", command=self.raise_bet)
      self.raise_button.grid(row=0, column=2, padx=10)

    def minimize_window(self):
        self.master.iconify()

    def close_window(self):
      self.master.destroy()
      
    def update_move(self,move):
      self.move_label.configure(text=move)
    
    def update_previousBet(self,prev):
      self.previousBet_label.configure(text="Previous bet: "+ str(prev))
    
    def update_hand(self, hand):
        self.player_hand_cards.configureure(text=" ".join(hand))

    def update_community(self, cards):
        self.community_cards.configure(text=" ".join(cards))

    def update_pot(self, pot):
        self.pot_label.configure(text=f"Pot: ${pot}")

    def update_status(self, status):
      self.status_label.configure(text=status)

    def fold(self):
      self.action_queue.put({"action":"fold","playerName":"human","amount":0})
      self.update_status("You folded")
    
    def call(self):
      self.action_queue.put({"action":"call","playerName":"human","amount":0}) #amt = 0, because prev bet stored in game.py
      self.update_status("You called.")
      

    def raise_bet(self):
      self.update_status("You raised")
      
