import customtkinter as ctk
from tkinter import messagebox
import Player


class PokerGUI:
  suitUniCodes = {"s":"\u2660","h":'\u2665',"c":'\u2663',"d":'\u2666'}
  
  def __init__(self, master,action_queue):
    
    self.playerTurn = False 
    self.action_queue = action_queue
    self.master = master
    #master.title("Poker")
    master.state('zoomed')        
    
    self.main_frame = ctk.CTkFrame(self.master)
    self.main_frame.pack(fill="both", expand=True)

    self.title_label = ctk.CTkLabel(self.main_frame, text="Poker", font=("Arial", 24))
    self.title_label.pack(pady=10)

    self.status_label = ctk.CTkLabel(self.main_frame, text="Welcome to Poker!", text_color="blue")
    self.status_label.pack(pady=10)
    
    self.move_label = ctk.CTkLabel(self.main_frame)#label to display player/bot moves
    self.move_label.pack(pady=10)
    
    self.previousBet_label = ctk.CTkLabel(self.main_frame)
    #self.previousBet_label.pack(pady=10)
    
    self.community_frame = ctk.CTkFrame(self.main_frame)
    self.community_frame.place(relx=0.5,rely=0.3,anchor="center")
    
    self.bot1_frame = ctk.CTkFrame(self.main_frame)
    self.bot1_frame.place(relx=0.15, rely=0.25, anchor="e")
    self.bot1_label = ctk.CTkLabel(self.bot1_frame, text="Bot1")
    self.bot1_label.grid(row=0,column=0,padx=5)
    self.bot1_money_label = ctk.CTkLabel(self.bot1_frame)
    self.bot1_money_label.grid(row=1,column=0,padx=5)
    
    self.bot2_frame = ctk.CTkFrame(self.main_frame)
    self.bot2_frame.place(relx=0.15, rely=0.60, anchor="e")
    self.bot2_label = ctk.CTkLabel(self.bot2_frame, text="Bot2")
    self.bot2_label.grid(row=0,column=0,padx=5)
    self.bot2_money_label = ctk.CTkLabel(self.bot2_frame)
    self.bot2_money_label.grid(row=1,column=0,padx=5)

    self.bot3_frame = ctk.CTkFrame(self.main_frame)
    self.bot3_frame.place(relx=0.85, rely=0.25, anchor="w")
    self.bot3_label = ctk.CTkLabel(self.bot3_frame, text="Bot3")
    self.bot3_label.grid(row=0,column=0,padx=5)
    self.bot3_money_label = ctk.CTkLabel(self.bot3_frame)
    self.bot3_money_label.grid(row=1,column=0,padx=5)

    self.bot4_frame = ctk.CTkFrame(self.main_frame)
    self.bot4_frame.place(relx=0.85, rely=0.60, anchor="w")
    self.bot4_label = ctk.CTkLabel(self.bot4_frame, text="Bot4")
    self.bot4_label.grid(row=0,column=0,padx=5)
    self.bot4_money_label = ctk.CTkLabel(self.bot4_frame)
    self.bot4_money_label.grid(row=1,column=0,padx=5)
    
    self.pot_label = ctk.CTkLabel(self.community_frame, text="Pot: $0")
    self.pot_label.grid(row=0,column=0,padx = 5)
    self.community_label = ctk.CTkLabel(self.community_frame, text="Community Cards:")
    self.community_label.grid(row=1, column=0, padx=5)
    self.community_cards = ctk.CTkLabel(self.community_frame, text="?")
    self.community_cards.grid(row=1, column=1, padx=5)
    
    
    self.player_frame = ctk.CTkFrame(self.main_frame)
    self.player_frame.place(relx=0.5, rely=0.60,anchor="center")
    
    
    self.player_hand_label = ctk.CTkLabel(self.player_frame, text="Your Hand:")
    self.player_hand_label.grid(row=0, column=0, padx=5)
    self.player_hand_cards = ctk.CTkLabel(self.player_frame, text="?")
    self.player_hand_cards.grid(row=0, column=1, padx=5)
    self.player_purse_label = ctk.CTkLabel(self.player_frame, text="Your Purse:")
    self.player_purse_label.grid(row=1,column=1,padx=5)

    
    self.action_frame = ctk.CTkFrame(self.main_frame)
    self.fold_button = ctk.CTkButton(self.action_frame, text="Fold", command=self.fold)
    self.fold_button.grid(row=0, column=0, padx=10)
    self.call_button = ctk.CTkButton(self.action_frame, text="Call", command=self.call)
    self.call_button.grid(row=0, column=1, padx=10)
    self.raise_button = ctk.CTkButton(self.action_frame, text="Raise", command=self.show_raise_entry)
    self.raise_button.grid(row=0, column=2, padx=10)
    
    self.entry_frame = ctk.CTkFrame(self.main_frame)
    self.raise_entry = ctk.CTkEntry(self.entry_frame,placeholder_text="Enter Bet Amount", width=150)
    self.raise_entry.grid(row=0, column=0, padx=10)
    self.submit_button = ctk.CTkButton(self.entry_frame,text="Submit Bet", command = self.raise_bet)
    self.submit_button.grid(row=1,column=0,padx=10)
    
    self.playerMoneyLabels = {1: self.player_purse_label,2:self.bot1_money_label,
                              3:self.bot2_money_label,4:self.bot3_money_label,
                              5:self.bot4_money_label}

  def minimize_window(self):
      self.master.iconify()

  def close_window(self):
    self.master.destroy()
    
  def update_move(self,move):
    self.move_label.configure(text=move)
  
  def update_previousBet(self,prev):
    self.previousBet_label.configure(text="Previous bet: "+ str(prev))
  
  def update_hand(self, hand):
    pretty = self.prettyPrint(hand)
    self.player_hand_cards.configure(text=pretty)
  
  def update_playerTurn(self,playerTurn):
    self.playerTurn = playerTurn
    if playerTurn:
      self.action_frame.place(relx=0.5,rely=0.7,anchor="center")
    else:
      self.action_frame.place_forget()
  
  def update_community(self, cards):
    pretty = self.prettyPrint(cards)
    self.community_cards.configure(text = pretty)

  def update_pot(self, pot):
    self.pot_label.configure(text=f"Pot: ${pot}")

  def update_status(self, status):
    self.status_label.configure(text=status)

  def fold(self):
    self.action_queue.put({"action":"fold","playerName":"human","amount":0})
    #self.update_status("You folded")
  
  def call(self):
    self.action_queue.put({"action":"call","playerName":"human","amount":0}) #amt = 0, because prev bet stored in game.py
    #self.update_status("You called.")
  
  def show_raise_entry(self):
    self.entry_frame.place(relx=0.5,rely=0.8,anchor="center")
    
  def raise_bet(self):
    amount = self.raise_entry.get()
    self.action_queue.put({"action":"raise","playerName":"human","amount":amount})
    self.entry_frame.place_forget()
  
  def prettyPrint(self,cards):
    text = ""
    face_map = {"1": "A", "11": "J", "12": "Q", "13": "K"}
    for card in cards:
      suit = card[0]
      unicode = self.suitUniCodes[suit]
      value = str(card[1:])
      number = face_map.get(value, value)
      pretty = number + unicode + " "
      text += pretty
    
    return text
  
  def updateMoney(self,player):
    label = self.playerMoneyLabels[player.playerID]
    label.configure(text = "Money: "+ str(player.money))
    
    
      
