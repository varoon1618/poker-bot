from GameEngine import PokerEngine
import uuid
from Bots import BotController
import pandas as pd
import numpy as np

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
          'player_chips': p.chips
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
    print(empirical_probs)
  
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
      print(f'P(WINNING/{k}) = {v}')  
    
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
    player_df = df[df['player_id'] == player_id].sort_values('game_id')
    pct_change = (player_df['player_chips'] - start_chips) / start_chips * 100
    return pct_change
  
  
if __name__ == "__main__":
  mc = MonteCarlo()
  df = mc.simulate_many_games(num_games=10000,save_df=False)
  #df = pd.read_pickle('500k_hands.pkl')
  df.to_pickle('50k_hands_with_player_data.pkl')
  #mc.estimate_hand_probability(df)
  #mc.estimate_bayesian_winning_probability(df)
  
  pct_change = mc.calculate_player_returns(df)
  
  print(f'mean return: {np.mean(pct_change)}%, std: {np.std(pct_change)}')
  
  #plt.plot(pct_change)
  #df.to_pickle('500k_hands.pkl')