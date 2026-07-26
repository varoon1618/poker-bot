import customtkinter as ctk
from tkinter import messagebox
import tkinter as tk


class PokerGUI:
  def __init__(self, master, engine):
    self.master = master
    self.engine = engine
    self.human_id = 1 #player id of the human player
    
    master.state('zoomed')
    self.main_frame = ctk.CTkFrame(master, fg_color="#2d9c2d")
    self.main_frame.pack(fill="both", expand=True)
    
    self._build_header()
    self._build_table()
    self._build_bots()
    self._build_player_area()
    self._build_action_controls()
    self._build_game_controls()
    
    #self._set_action_buttons_state("disabled")
  
  def _build_header(self):
    # Title
    self.title_label = ctk.CTkLabel(self.main_frame, text="Poker", font=("Arial", 24))
    self.title_label.pack(pady=10)
    
    # Status label (displays game state messages like "Preflop", "Flop", etc.)
    self.status_label = ctk.CTkLabel(self.main_frame, text="Welcome to Poker!", text_color="blue")
    self.status_label.pack(pady=10)
    
    # Move label (displays what each player/bot did)
    self.move_label = ctk.CTkLabel(self.main_frame, text="")
    self.move_label.pack(pady=10)  
  
  def _build_player_area(self):
    # Main frame for the human player's information
    self.player_frame = ctk.CTkFrame(self.main_frame, fg_color="#ccffcc")
    self.player_frame.place(relx=0.5, rely=0.60, anchor="center")
    
    # Label: "Your Hand:"
    self.player_hand_label = ctk.CTkLabel(self.player_frame, text="Your Hand:")
    self.player_hand_label.grid(row=0, column=0, padx=5, sticky="e")
    
    # Label displaying the actual cards (initially "?")
    self.player_hand_cards = ctk.CTkLabel(self.player_frame, text="?")
    self.player_hand_cards.grid(row=0, column=1, padx=5, sticky="w")
    
    # Label for the player's chip count (spans both columns for full width)
    self.player_purse_label = ctk.CTkLabel(self.player_frame, text="Your Purse: £1000")
    self.player_purse_label.grid(row=1, column=0, columnspan=2, padx=5, sticky="we")
    
    # Configure grid columns to expand evenly (keeps the layout clean)
    self.player_frame.grid_columnconfigure(0, weight=1)
    self.player_frame.grid_columnconfigure(1, weight=1)
  
  def _build_action_controls(self):
    # --- Main action frame (Fold, Call, Raise) ---
    self.action_frame = ctk.CTkFrame(self.main_frame, fg_color="#ccffcc")
    self.action_frame.place(relx=0.5, rely=0.80, anchor="center")
    
    self.fold_button = ctk.CTkButton(
        self.action_frame, 
        text="Fold", 
        command=self.fold,
        width=80
    )
    self.fold_button.grid(row=0, column=0, padx=10, pady=5)
    
    self.call_button = ctk.CTkButton(
        self.action_frame, 
        text="Call", 
        command=self.call,
        width=80
    )
    self.call_button.grid(row=0, column=1, padx=10, pady=5)
    
    self.raise_button = ctk.CTkButton(
        self.action_frame, 
        text="Raise", 
        command=self.show_raise_entry,
        width=80
    )
    self.raise_button.grid(row=0, column=2, padx=10, pady=5)
    
    # --- Separate frame for the Raise Entry (hidden by default) ---
    self.entry_frame = ctk.CTkFrame(self.main_frame, fg_color="#ccffcc")
    self.entry_frame.place(relx=0.5, rely=0.87, anchor="center")
    self.entry_frame.grid_remove()  # Hides it initially (unlike pack_forget)
    
    self.raise_entry = ctk.CTkEntry(
        self.entry_frame, 
        placeholder_text="Enter Bet Amount", 
        width=150
    )
    self.raise_entry.grid(row=0, column=0, padx=10)
    
    self.submit_bet_button = ctk.CTkButton(
        self.entry_frame, 
        text="Submit Bet", 
        command=self.raise_bet,
        width=80
    )
    self.submit_bet_button.grid(row=1, column=0, padx=10, pady=5)
  
  def _build_game_controls(self):
    self.continue_frame = ctk.CTkFrame(self.main_frame, fg_color="#ccffcc")
    self.continue_frame.place(relx=0.5, rely=0.93, anchor="center")
    
    self.continue_button = ctk.CTkButton(
        self.continue_frame, 
        text="Continue Playing", 
        command=self.continue_playing,
        width=150
    )
    self.continue_button.grid(row=0, column=0, padx=10, pady=5)
    
    self.end_game_button = ctk.CTkButton(
        self.continue_frame, 
        text="End Game", 
        command=self.end_game,
        width=150,
        fg_color="#d9534f",  # Red color to signal "quit"
        hover_color="#c9302c"
    )
    self.end_game_button.grid(row=1, column=0, padx=10, pady=5)
    
  def _build_table(self):
    self.community_frame = ctk.CTkFrame(self.main_frame, fg_color="#ccffcc")
    self.community_frame.place(relx=0.5, rely=0.3, anchor="center")
    
    self.pot_label = ctk.CTkLabel(self.community_frame, text="Pot: £0")
    self.pot_label.grid(row=0, column=0, columnspan=2, sticky="we")
    
    ctk.CTkLabel(self.community_frame, text="Community Cards:").grid(row=1, column=0, sticky="e")
    self.community_cards_label = ctk.CTkLabel(self.community_frame, text="?")
    self.community_cards_label.grid(row=1, column=1, sticky="w")
    
    ctk.CTkLabel(self.community_frame, text="Current Bet:").grid(row=2, column=0, sticky="e")
    self.current_bet_label = ctk.CTkLabel(self.community_frame, text="0")
    self.current_bet_label.grid(row=2, column=1, sticky="w")
  
  def _build_bots(self):
    bot_positions = [
        {"id": 2, "name": "Bot 1", "relx": 0.15, "rely": 0.25, "anchor": "e"},
        {"id": 3, "name": "Bot 2", "relx": 0.15, "rely": 0.60, "anchor": "e"},
        {"id": 4, "name": "Bot 3", "relx": 0.85, "rely": 0.60, "anchor": "w"},
        {"id": 5, "name": "Bot 4", "relx": 0.85, "rely": 0.25, "anchor": "w"},
    ]
    
    self.bot_widgets = {} 
    
    for pos in bot_positions:
      pid = pos["id"]
      frame = ctk.CTkFrame(self.main_frame, fg_color="#ccffcc")
      frame.place(relx=pos["relx"], rely=pos["rely"], anchor=pos["anchor"])
      
      # Store everything in a nested dict for easy access later
      self.bot_widgets[pid] = {
          "frame": frame,
          "name_label": ctk.CTkLabel(frame, text=pos["name"]),
          "money_label": ctk.CTkLabel(frame, text="£1000"),
          "action_label": ctk.CTkLabel(frame, text="Action: "),
          "hand_label": ctk.CTkLabel(frame, text="Hand: ?")
      }
      
      self.bot_widgets[pid]["name_label"].grid(row=0, column=0, padx=5)
      self.bot_widgets[pid]["money_label"].grid(row=1, column=0, padx=5)
      self.bot_widgets[pid]["action_label"].grid(row=2, column=0, padx=5)
      self.bot_widgets[pid]["hand_label"].grid(row=3, column=0, padx=5)
  
  def _trigger_call(self):
    self._process_action(self.human_id,"CALL")
    self._disable_action_buttons()
  
  def _trigger_fold(self):
    self._process_action(self.human_id,"FOLD")
    self._disable_action_buttons()
  
  def _trigger_raise(self):
    amount = int(self.raise_entry.get())
    self._process_action(self.human_id,"RAISE",amount=amount)
    self._disable_action_buttons()
    
  def _process_action(self,id,action,amount=None):
    self.engine.handle_action(id,action,amount)
  
  def _disable_action_buttons(self):
    """Disables the main action buttons (Fold, Call, Raise)."""
    self.fold_button.configure(state="disabled")
    self.call_button.configure(state="disabled")
    self.raise_button.configure(state="disabled")
    
    # Also hide the raise entry box if it happens to be open
    self.entry_frame.grid_remove()
    self.raise_entry.delete(0, "end")
  
  def _enable_action_buttons(self):
    """Enables the main action buttons (Fold, Call, Raise)."""
    self.fold_button.configure(state="normal")
    self.call_button.configure(state="normal")
    self.raise_button.configure(state="normal")
  

if __name__ == "__main__":
  root = tk.Tk()
  gui = PokerGUI(root,engine=None)
  root.mainloop()