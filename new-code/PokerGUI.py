import customtkinter as ctk
from tkinter import messagebox
import tkinter as tk
from PokerEngine import PokerEngine
import logging
from BotController import BotController

ctk.set_appearance_mode("Light")          # Light mode for crispness
ctk.set_default_color_theme("green")      # Built‑in green theme

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class PokerGUI:
  def __init__(self, master, engine):
    self.master = master
    self.engine = engine
    self.human_id = 0
    self.bot_controller = BotController()

    master.state('zoomed')
    self.main_frame = ctk.CTkFrame(master, fg_color="#2d9c2d")   # kept original green
    self.main_frame.pack(fill="both", expand=True)

    self._build_header()
    self._build_table()
    self._build_bots()
    self._build_player_area()
    self._build_action_controls()
    #self._build_game_controls()

  def _build_header(self):
    # Title – larger, bold, with subtle shadow effect (via border)
    self.title_label = ctk.CTkLabel(
        self.main_frame,
        text="♠ Poker ♥",
        font=("Arial", 28, "bold"),
        text_color="#ffffff"  # white on green background
    )
    self.title_label.pack(pady=(15, 5))

    # Status label – now with a semi‑transparent background and rounded corners
    self.status_label = ctk.CTkLabel(
        self.main_frame,
        text="Welcome to Poker!",
        font=("Arial", 16, "bold"),
        fg_color="#3cb371",          # medium sea green, matches theme
        text_color="white",
        corner_radius=8,
        padx=20,
        pady=5
    )
    self.status_label.pack(pady=(5, 10))

    # Move label – nicer background, bold font
    self.move_label = ctk.CTkLabel(
        self.main_frame,
        text="Latest Move: ",
        font=("Arial", 14),
        fg_color="#5bb5ec",           # kept your blue
        text_color="white",
        corner_radius=6,
        padx=15,
        pady=4
    )
    self.move_label.pack(pady=(5, 10))

  # ------------------- COMMUNITY TABLE -------------------
  def _build_table(self):
    self.community_frame = ctk.CTkFrame(
        self.main_frame,
        fg_color="#d4edda",           # softer light green (was #ccffcc)
        corner_radius=12,
        border_width=2,
        border_color="#28a745",
        width = 320,
        height = 170
    )
    self.community_frame.place(relx=0.5, rely=0.35, anchor="center")
    self.community_frame.grid_propagate(False)
    self.community_frame.grid_columnconfigure(0, weight=1)
    
    # Pot label – larger and bold
    self.pot_label = ctk.CTkLabel(
        self.community_frame,
        text="Pot: £0",
        font=("Arial", 16, "bold"),
        text_color="#155724",
        wraplength = 80
    )
    self.pot_label.grid(row=0, column=0, columnspan=2, sticky="", pady=5)

    # Community cards – with better spacing
    ctk.CTkLabel(
        self.community_frame,
        text="Community Cards:",
        font=("Arial", 16, "bold"),
        text_color="#155724"
    ).grid(row=1, column=0, sticky="w", padx=5, pady=2)

    self.community_cards_label = ctk.CTkLabel(
        self.community_frame,
        text="?",
        font=("Arial", 16),
        text_color="#155724"
    )
    self.community_cards_label.grid(row=1, column=1, sticky="w", padx=5, pady=2)

    self.bet_text_label = ctk.CTkLabel(
        self.community_frame,
        text="Current Bet:",
        font=("Arial", 16, "bold"),
        text_color="#155724"
    )
    
    self.bet_text_label.grid(row=2, column=0, sticky="w", padx=5, pady=2)

    self.current_bet_label = ctk.CTkLabel(
        self.community_frame,
        text="0",
        font=("Arial", 16),
        text_color="#155724"
    )
    self.current_bet_label.grid(row=2, column=1, sticky="", padx=5, pady=2)

    # Add some internal padding to the frame
    for child in self.community_frame.winfo_children():
        child.grid_configure(pady=3)   # consistent vertical spacing

  # ------------------- BOT WIDGETS -------------------
  def _build_bots(self):
    bot_positions = [
        {"id": 4, "name": "Bot 4", "relx": 0.15, "rely": 0.25, "anchor": "e"},
        {"id": 3, "name": "Bot 3", "relx": 0.15, "rely": 0.60, "anchor": "e"},
        {"id": 2, "name": "Bot 2", "relx": 0.85, "rely": 0.60, "anchor": "w"},
        {"id": 1, "name": "Bot 1", "relx": 0.85, "rely": 0.25, "anchor": "w"},
    ]

    self.bot_widgets = {}

    for pos in bot_positions:
      pid = pos["id"]
      frame = ctk.CTkFrame(
          self.main_frame,
          fg_color="#d4edda",
          corner_radius=10,
          border_width=1,
          border_color="#28a745",
          width = 150
      )
      frame.place(relx=pos["relx"], rely=pos["rely"], anchor=pos["anchor"])
      frame.grid_propagate(False)     
      frame.grid_columnconfigure(0, weight=1)
           
      # Store widgets
      self.bot_widgets[pid] = {
          "frame": frame,
          "name_label": ctk.CTkLabel(
              frame,
              text=pos["name"],
              font=("Arial", 16, "bold"),
              text_color="#155724"
          ),
          "money_label": ctk.CTkLabel(
              frame,
              text="£1000",
              font=("Arial", 14),
              text_color="#155724"
          ),
          "action_label": ctk.CTkLabel(
              frame,
              text="Action: ",
              font=("Arial", 14),
              text_color="#155724"
          ),
          "hand_label": ctk.CTkLabel(
              frame,
              text="Hand: ?",
              font=("Arial", 14),
              text_color="#155724"
          )
      }

      # Grid layout with better spacing
      self.bot_widgets[pid]["name_label"].grid(row=0, column=0, padx=8, pady=(6, 2), sticky="")
      self.bot_widgets[pid]["money_label"].grid(row=1, column=0, padx=8, pady=2, sticky="")
      self.bot_widgets[pid]["action_label"].grid(row=2, column=0, padx=8, pady=2, sticky="w")
      self.bot_widgets[pid]["hand_label"].grid(row=3, column=0, padx=8, pady=(2, 6), sticky="w")

  # ------------------- HUMAN PLAYER AREA -------------------
  def _build_player_area(self):
    self.player_frame = ctk.CTkFrame(
        self.main_frame,
        fg_color="#d4edda",
        corner_radius=12,
        border_width=2,
        border_color="#28a745",
    )
    self.player_frame.place(relx=0.5, rely=0.60, anchor="center")

    # "Your Hand:" – bold
    self.player_hand_label = ctk.CTkLabel(
        self.player_frame,
        text="Your Hand:",
        font=("Arial", 16, "bold"),
        text_color="#155724"
    )
    self.player_hand_label.grid(row=0, column=0, padx=8, pady=8, sticky="e")

    self.player_hand_cards = ctk.CTkLabel(
        self.player_frame,
        text="?",
        font=("Arial", 16),
        text_color="#155724"
    )
    self.player_hand_cards.grid(row=0, column=1, padx=8, pady=8, sticky="w")

    self.player_purse_label = ctk.CTkLabel(
        self.player_frame,
        text="Your Purse: £1000",
        font=("Arial", 16, "bold"),
        text_color="#155724"
    )
    self.player_purse_label.grid(row=1, column=0, columnspan=2, padx=8, pady=(0, 8), sticky="we")

    self.player_frame.grid_columnconfigure(0, weight=1)
    self.player_frame.grid_columnconfigure(1, weight=1)

  def _build_action_controls(self):
    # Main action frame (Fold, Call, Raise)
    self.action_frame = ctk.CTkFrame(
        self.main_frame,
        fg_color="#d4edda",
        corner_radius=12,
        border_width=2,
        border_color="#28a745"
    )
    self.action_frame.place(relx=0.5, rely=0.70, anchor="center")

    # Buttons with hover effects and rounded corners
    self.fold_button = ctk.CTkButton(
        self.action_frame,
        text="Fold",
        command=self._trigger_fold,
        width=90,
        height=35,
        corner_radius=8,
        fg_color="#dc3545",          # red for fold
        hover_color="#c82333",
        text_color="white"
    )
    self.fold_button.grid(row=0, column=0, padx=10, pady=8)

    self.call_button = ctk.CTkButton(
        self.action_frame,
        text="Call",
        command=self._trigger_call,
        width=90,
        height=35,
        corner_radius=8,
        fg_color="#0e74e0",          # green for call
        hover_color="#0757ac",
        text_color="white"
    )
    self.call_button.grid(row=0, column=1, padx=10, pady=8)

    self.raise_button = ctk.CTkButton(
        self.action_frame,
        text="Raise",
        command=self._show_raise_entry,
        width=90,
        height=35,
        corner_radius=8,
        fg_color="#ffc107",          # yellow/amber for raise
        hover_color="#e0a800",
        text_color="black"
    )
    self.raise_button.grid(row=0, column=2, padx=10, pady=8)

    # --- Raise Entry (separate frame, hidden by default) ---
    self.entry_frame = ctk.CTkFrame(
        self.main_frame,
        fg_color="#d4edda",
        corner_radius=10,
        border_width=1,
        border_color="#28a745"
    )
    self.entry_frame.place(relx=0.5, rely=0.8, anchor="center")
    self.entry_frame.place_forget()

    self.raise_entry = ctk.CTkEntry(
        self.entry_frame,
        placeholder_text="Enter Bet Amount",
        width=160,
        height=30,
        corner_radius=8,
        border_color="#28a745",
        fg_color="white"
    )
    self.raise_entry.grid(row=0, column=0, padx=15, pady=(10, 5))

    self.submit_bet_button = ctk.CTkButton(
        self.entry_frame,
        text="Submit Bet",
        command=self._trigger_raise,
        width=90,
        height=32,
        corner_radius=8,
        fg_color="#17a2b8",          # teal for submit
        hover_color="#138496",
        text_color="white"
    )
    self.submit_bet_button.grid(row=1, column=0, padx=15, pady=(0, 10))

  # ------------------- GAME CONTROLS -------------------
  def _enable_game_controls(self):
    self.continue_frame = ctk.CTkFrame(
        self.main_frame,
        fg_color="#d4edda",
        corner_radius=12,
        border_width=2,
        border_color="#28a745"
    )
    self.continue_frame.place(relx=0.5, rely=0.93, anchor="center")

    self.continue_button = ctk.CTkButton(
        self.continue_frame,
        text="Continue Playing",
        command=self._continue_playing,
        width=160,
        height=36,
        corner_radius=8,
        fg_color="#0a8426",
        hover_color="#0E6A22",
        text_color="white"
    )
    self.continue_button.grid(row=0, column=0, padx=12, pady=8)

    self.end_game_button = ctk.CTkButton(
        self.continue_frame,
        text="Restart New Game",
        command=self._restart_game,
        width=160,
        height=36,
        corner_radius=8,
        fg_color="#d9534f",          # kept red
        hover_color="#c9302c",
        text_color="white"
    )
    self.end_game_button.grid(row=1, column=0, padx=12, pady=(0, 8))
  
  def _disable_game_controls(self):
    if hasattr(self, 'continue_frame') and self.continue_frame:
      self.continue_frame.place_forget()
  
  def _trigger_call(self):
    self._process_action("CALL")

  def _trigger_fold(self):
    self._process_action("FOLD")
    #self._disable_action_buttons()

  def _trigger_raise(self):
    amount = int(self.raise_entry.get())
    self._process_action("RAISE", amount=amount)
    self._clear_raise_entry()

  def _format_cards(self, cards):
    return " ".join(str(c) for c in cards)

  def _process_action(self, action, amount=0):
    self.engine.handle_action(action, amount)
  
  def _clear_raise_entry(self):
    self.raise_entry.delete(0,"end")
    
  def _disable_action_buttons(self):
    self.fold_button.configure(state="disabled")
    self.call_button.configure(state="disabled")
    self.raise_button.configure(state="disabled")
    self.entry_frame.place_forget()
    self.raise_entry.delete(0, "end")

  def _show_raise_entry(self):
    self.raise_entry.delete(0, "end")
    self.entry_frame.place(relx=0.5, rely=0.87, anchor="center")
    self.raise_entry.focus_set()

  def _enable_action_buttons(self):
    self.call_button.configure(text="Call", width=90,fg_color="#17a2b8",hover_color="#138496",)
    self.call_button.grid(row=0, column=1, padx=10, pady=8, columnspan=1)
    self.fold_button.grid() 
    self.raise_button.grid()     
    self.fold_button.configure(state="normal")
    self.call_button.configure(state="normal")
    self.raise_button.configure(state="normal")
  
  def _build_buy_in_button(self):
    self.call_button.configure(text="Buy In", width=200, fg_color="#6f42c1", hover_color="#5a32a3")
    self.call_button.grid(row=0, column=0, padx=10, pady=8, columnspan=3)
    self.fold_button.grid_remove()
    self.raise_button.grid_remove()

    
  def _enable_buy_in_button(self):
    self.call_button.configure(state="normal")
    
  def update_display(self, state):
    self.pot_label.configure(text=f"Pot: £{state.pot}")
    bet_text = ""
    if state.round == 'BUY_IN':
      bet_text = f'Buy in Price: '
    else:
      bet_text = f'Current Bet: '
    self.bet_text_label.configure(text = bet_text)
    self.current_bet_label.configure(text = f'£{state.prev_bet}')
    
    self.community_cards_label.configure(text=self._format_cards(state.community_cards))
    
    human_player = next(p for p in state.players if p.id == self.human_id)
    self.player_purse_label.configure(text=f"Your Purse: £{human_player.chips}")
    self.player_hand_cards.configure(text=self._format_cards(human_player.hand))
    
    #logger.info(f'round:{state.round}, new_round:{state.new_round}')
    
    for i in range(5):
      player = state.players[i]
      if player.id == self.human_id:
        continue
      
      self._clear_bot_hand_label(player)
      self._update_bot_money_label(player)
      self._update_bot_action_label(player)
    
    self._un_highlight_all_bots()
    
    if state.round == 'BUY_IN':
      self._build_buy_in_button()
    
    if state.current_player.id == self.human_id:
      if state.round == 'BUY_IN':
        self._enable_buy_in_button()
      else:
        self._enable_action_buttons()
    else:
      if not(state.game_complete):
        self._highlight_bot_frame(state.current_player.id)
        
        if state.round != 'BUY_IN':
          self._disable_action_buttons()
        else:
          self.call_button.configure(state="disabled")
    
    self.status_label.configure(text=f"Round: {state.round}")
    
    if state.round == 'SHOWDOWN':
      self._show_active_player_hands(state.players)
    
    t = ""
    if state.game_complete:
      t = self._format_winning_text(state.winners,state.winning_rank_name)
    elif not(state.game_complete) and state.exception is None :
      t = 'Your Move' if state.current_player.id == 0 else f'Bot {state.current_player.id}\'s Move'
    else:
      t = state.exception
    
    self.move_label.configure(text=t)

    if state.current_player.id != self.human_id:
      if not(state.game_complete):
        self.master.after(500, self._trigger_bot_move, state)
    
    if state.game_complete:
      self._enable_game_controls()
      
  def _clear_bot_action_label(self,bot):    
    self.bot_widgets[bot.id]['action_label'].configure(text="Action: ") 
  
  def _clear_bot_hand_label(self,bot):   
    self.bot_widgets[bot.id]['hand_label'].configure(text="Hand: ?") 
  
  def _format_winning_text(self,winners,rank_name):
    names = [str(p) for p in winners]
    message = " and ".join(names) + " won"
    
    if rank_name:
      rname = rank_name.lower().replace('_',' ')
      message += f" by {str(rname)}"
    
    return message
  
  def _update_bot_money_label(self,bot):
    self.bot_widgets[bot.id]["money_label"].configure(text=f"£{bot.chips}")
    
  def _update_bot_action_label(self,bot):
    s = "Action: "
    if bot.latest_action == 'BUY_IN':
      s = f'Action: Bought in'
    
    elif bot.latest_action == "CALL":
      s = f'Action: Called £{bot.current_bet}'
        
    elif bot.latest_action == 'FOLD':
      s = f'Action: Folded'
        
    elif bot.latest_action == "RAISE":
      s = f'Action: Raised £{bot.current_bet}'
    
    self.bot_widgets[bot.id]['action_label'].configure(text=s) 
    
  def _show_active_player_hands(self,players):
    for p in players:
      if p.id == self.human_id or p.has_folded:
        continue
      
      text = f'Hand: {self._format_cards(p.hand)}'
      self.bot_widgets[p.id]['hand_label'].configure(text=text)

  def _continue_playing(self):
    self.engine.initialise_game()
    self._disable_game_controls()
    pass

  def _end_game(self):
    self._disable_game_controls()
    pass
  
  def _restart_game(self):
    self._disable_game_controls()
    self.engine = PokerEngine()
    self.engine.register_listener(self.update_display)
    self.engine.initialise_game()

  def _trigger_bot_move(self, state):
    action, amount = self.bot_controller.make_decision(state)
    self._process_action(action, amount)
  
  def _highlight_bot_frame(self, bot_id, thick=True):
    default_border_color = "#28a745"
    highlight_color = "red"
    default_width = 1
    highlight_width = 3   # thicker when highlighted
    
    if bot_id in self.bot_widgets:
        self.bot_widgets[bot_id]['frame'].configure(
            border_color=highlight_color,
            border_width=highlight_width if thick else default_width
        )
  
  def _un_highlight_all_bots(self):
    default_border_color = "#28a745"
    for pid in self.bot_widgets:
            self.bot_widgets[pid]['frame'].configure(
                border_color=default_border_color,
                border_width=1
            )
if __name__ == "__main__":
    root = tk.Tk()
    poker_engine = PokerEngine()
    gui = PokerGUI(root, engine=poker_engine)
    poker_engine.register_listener(gui.update_display)
    poker_engine.initialise_game()
    root.mainloop()