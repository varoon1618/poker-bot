import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from GameEngine import PokerEngine
from Bots import BotController
import pandas as pd
import numpy as np
import uuid
import matplotlib.pyplot as plt

class GameData:
  @classmethod
  def from_game_state(cls,state):
    game_id = uuid.uuid4()
    winners = state.winners
    winning_rank = state.winning_rank_name
    players = state.players
    ranks_seen = ['HIGH_CARD' if p.hand_rank is None else p.hand_rank.rank_name for p in players]
    
    return cls(winners=winners,winning_rank=winning_rank,ranks_seen=ranks_seen,game_id=game_id,
               players=players)
  
  def __init__(self,**kwargs):
    self.winners = kwargs.get('winners',[])
    self.game_id = kwargs.get('game_id')
    self.winning_rank = kwargs.get('winning_rank')
    self.ranks_seen = kwargs.get('ranks_seen')
    self.players = kwargs.get('players', [])
  
  def generate_rows(self):
    winner_ids = {p.id for p in self.winners} if self.winners else set()
    rows = []
    for p, rank in zip(self.players, self.ranks_seen):
      rows.append({
          'game_id': self.game_id,
          'player_id': p.id,
          'hand_rank': rank,
          'is_winner': p.id in winner_ids,
          'player_chips': p.chips,
          'player_strategy':p.strategy
      })
    return rows  

class MonteCarlo:
  def __init__(self):
    self.games = []
    self.rows = []
    self.bot_controller = BotController()
    pass
  
  def update_data(self,state):
    if state.game_complete:
      game_data = GameData.from_game_state(state)
      rows = game_data.generate_rows()
      self.rows.extend(rows)
    else:
      self.process_action(state)
  
  def process_action(self,state):
    if not(state.can_continue_betting) and state.round != 'SHOWDOWN':
      self.engine._advance_round()
      return
    
    if state.round == 'BUY_IN':
      action = "CALL"
      amount = 0
    else:
      action, amount = self.bot_controller.make_decision(state)
    
    self.engine.handle_action(action=action,amount=amount)
  
  def simulate_one_game(self):
    self.engine = PokerEngine()
    self.engine.register_listener(self.update_data)
    self.engine.initialise_game()
  
  def simulate_many_games(self,num_games=1000,save_df=False,df_name=None):
    if not(df_name):
      df_name = uuid.uuid4()
    
    for _ in range(num_games):
      self.simulate_one_game()
    
    df = pd.DataFrame(self.rows)
    
    if save_df:
      df.to_pickle(df_name)
    
    return df
  
  def estimate_hand_probability(self,df):
    empirical_probs = df['hand_rank'].value_counts(normalize=True)
    df_probs = empirical_probs.reset_index()
    df_probs.columns = ['Hand Rank', 'Probability']
    df_probs['Probability'] = df_probs['Probability'].apply(lambda x: f"{x:.4%}")
    print(df_probs.to_string(index=False))

  
  def estimate_bayesian_winning_probability(self,df):
    ranks = df['hand_rank'].unique()
    out = {}
    for r_type in ranks:
      total = df[df['hand_rank'] == r_type] #num of times rank was seen from all individual hands
      count = len(total)
      
      won = len(total[total['is_winner'] == True]) #num of times rank actually won 
      
      prob_win_given_r = won / count  # P(winning/rank_type)
      out[r_type] = prob_win_given_r
    
    for k,v in out.items():
      print(f'P(WINNING/{k}) = {v:.4%}')  
    
    return out
  
  def calculate_player_winning_probabilties(self,df):
    ids = [0,1,2,3,4]
    p_win_probs= {}
    for id in ids:
      total = df[df['player_id'] == id]
      
      count = len(total)
      won  = len(df[df['is_winner']==True])
      
      prob = won/count
      p_win_probs[id] =  prob
    
    for k,v in p_win_probs.items():
      print(f'Player: {k}, winning prob: {v*100:.4f}%')
  
    return p_win_probs  
  
  def calculate_player_returns(self,df,player_id=0,start_chips=1000):
    player_df = df[df['player_id'] == player_id]
    pct_change = (df['player_chips'] - start_chips) / start_chips * 100
    return pct_change
  
 
def plot_cum_profit(df,player_id=0):
  df['returns'] = df['player_chips'] - 1000
  player_df = df[df['player_id'] == player_id]
  cumulative = player_df['returns'].cumsum()
  plt.figure(figsize=(12, 6))
  plt.plot(cumulative,linewidth=2, color='green')
  plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)  # Baseline
  plt.title("Combinatorial Strategy Cumulative Profit")
  plt.xlabel("Hand Number")
  plt.ylabel("Cumulative Profit (£)")
  plt.grid(True, alpha=0.3)
  plt.show()

def plot_pct_returns(df,player_id=0):
  player_df = df[df['player_id'] == player_id]
  returns_pct = (player_df['player_chips'] - 1000) / 1000 * 100
  plt.figure(figsize=(12, 4))
  plt.plot(returns_pct, linewidth=1, color='blue', markersize=3)
  plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
  plt.title("% Returns Per Hand")
  plt.xlabel("Hand Number")
  plt.ylabel("Returns (%)")
  plt.grid(True, alpha=0.3)
  plt.show()

  
if __name__ == "__main__":
  mc = MonteCarlo()
  df = mc.simulate_many_games(num_games=200,save_df=True,df_name='200k_hands.pkl')
  
  #df = pd.read_pickle('50k_hands.pkl')
  
  mc.estimate_hand_probability(df)
  print()
  mc.estimate_bayesian_winning_probability(df)
    
  id = 2
  plot_cum_profit(df,player_id=id)
  plot_pct_returns(df,player_id=id)
  