from PokerEngine import PokerEngine
import uuid
import pandas as pd
class GameData:
  @classmethod
  def from_game_state(cls,state):
    game_id = uuid.uuid4()
    winners = state.winners
    winning_rank = state.winning_rank_name
    players = state.players
    ranks_seen = [p.hand_rank.rank_name for p in players]
    player_ids = [p.id for p in players]
    
    return cls(winners=winners,winning_rank=winning_rank,ranks_seen=ranks_seen,game_id=game_id,
               player_ids=player_ids)
  
  def __init__(self,**kwargs):
    self.winners = kwargs.get('winners',[])
    self.game_id = kwargs.get('game_id')
    self.winning_rank = kwargs.get('winning_rank')
    self.ranks_seen = kwargs.get('ranks_seen')
    self.player_ids = kwargs.get('player_ids', [])
  
  def generate_rows(self):
    winner_ids = {p.id for p in self.winners} if self.winners else set()
    rows = []
    for pid, rank in zip(self.player_ids, self.ranks_seen):
      rows.append({
          'game_id': self.game_id,
          'player_id': pid,
          'hand_rank': rank,
          'is_winner': pid in winner_ids
      })
    return rows  

class MonteCarlo:
  def __init__(self):
    self.games = []
    self.rows = []
    pass
  
  def update_data(self,state):
    if state.game_complete:
      game_data = GameData.from_game_state(state)
      rows = game_data.generate_rows()
      self.rows.extend(rows)
    else:
      self.process_action()
  
  def process_action(self):
    self.engine.handle_action(action='CALL',amount=5)
  
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
  

if __name__ == "__main__":
    mc = MonteCarlo()
    #df = mc.simulate_many_games(num_games=100000,save_df=False)
    #df = pd.read_pickle('500k_hands.pkl')
    mc.estimate_hand_probability(df)
    mc.estimate_bayesian_winning_probability(df)
    #df.to_pickle('500k_hands.pkl')