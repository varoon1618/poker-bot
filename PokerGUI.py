import tkinter as tk
from tkinter import messagebox

class PokerGUI:
    def __init__(self, master):
        self.master = master
        master.title("Poker Game")
        master.geometry("600x400")

        self.title_label = tk.Label(master, text="Poker Game", font=("Arial", 24))
        self.title_label.pack(pady=10)

        self.player_frame = tk.Frame(master)
        self.player_frame.pack(pady=10)

        self.player_hand_label = tk.Label(self.player_frame, text="Your Hand:")
        self.player_hand_label.grid(row=0, column=0, padx=5)
        self.player_hand_cards = tk.Label(self.player_frame, text="?")
        self.player_hand_cards.grid(row=0, column=1, padx=5)

        self.community_frame = tk.Frame(master)
        self.community_frame.pack(pady=10)
        self.community_label = tk.Label(self.community_frame, text="Community Cards:")
        self.community_label.grid(row=0, column=0, padx=5)
        self.community_cards = tk.Label(self.community_frame, text="?")
        self.community_cards.grid(row=0, column=1, padx=5)

        self.pot_label = tk.Label(master, text="Pot: $0")
        self.pot_label.pack(pady=5)

        self.action_frame = tk.Frame(master)
        self.action_frame.pack(pady=20)
        self.fold_button = tk.Button(self.action_frame, text="Fold", command=self.fold)
        self.fold_button.grid(row=0, column=0, padx=10)
        self.call_button = tk.Button(self.action_frame, text="Call", command=self.call)
        self.call_button.grid(row=0, column=1, padx=10)
        self.raise_button = tk.Button(self.action_frame, text="Raise", command=self.raise_bet)
        self.raise_button.grid(row=0, column=2, padx=10)

        self.status_label = tk.Label(master, text="Welcome to Poker!", fg="blue")
        self.status_label.pack(pady=10)

    def update_hand(self, hand):
        self.player_hand_cards.config(text=" ".join(hand))

    def update_community(self, cards):
        self.community_cards.config(text=" ".join(cards))

    def update_pot(self, pot):
        self.pot_label.config(text=f"Pot: ${pot}")

    def update_status(self, status):
        self.status_label.config(text=status)

    def fold(self):
        self.update_status("You folded.")
        messagebox.showinfo("Action", "You folded.")

    def call(self):
        self.update_status("You called.")
        messagebox.showinfo("Action", "You called.")

    def raise_bet(self):
        self.update_status("You raised.")
        messagebox.showinfo("Action", "You raised.")

if __name__ == "__main__":
    root = tk.Tk()
    gui = PokerGUI(root)
    # Example usage:
    gui.update_hand(["h10", "s2"])
    gui.update_community(["c5", "d7", "h3"])
    gui.update_pot(150)
    root.mainloop()
