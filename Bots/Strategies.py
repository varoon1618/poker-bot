from abc import ABC, abstractmethod
from GameElements import GameState
import math
from collections import Counter
from .ProbabilityEstimator import ProbabilityEstimator
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)  

class BotStrategy(ABC):
  @abstractmethod
  def decide(self,state:GameState):
    '''Takes in Gamestate, and returns 
    Action (CALL,FOLD,RAISE), with optional AMOUNT'''
    pass

class CombinatorialStrategy(BotStrategy):  
  def __init__(self):
    self.estimator = ProbabilityEstimator()
    #P(WINNING/ROYAL_FLUSH).. etc
    # precomputed from running sims of 500,000 hands
    self.bayesian_probabilities = {
      'ROYAL_FLUSH': 1.0,
      'STRAIGHT_FLUSH': 1.0,
      'FOUR_OF_A_KIND': 0.9974715549936789,
      'FULL_HOUSE': 0.8496703926626541,
      'FLUSH': 0.6956635318704284,
      'STRAIGHT': 0.8121512709237446,
      'THREE_OF_A_KIND': 0.5670867795720099,
      'TWO_PAIR': 0.291366693956095,
      'ONE_PAIR': 0.09366430491953859,
      'HIGH_CARD': 0.002596154945846724
    }
    
    self.rank_types = [
      'ROYAL_FLUSH',
      'STRAIGHT_FLUSH',
      'FOUR_OF_A_KIND',
      'FULL_HOUSE',
      'FLUSH',
      'STRAIGHT',
      'THREE_OF_A_KIND',
      'TWO_PAIR',
      'ONE_PAIR',
      'HIGH_CARD'
    ]
    
    self.estimate_call_backs = {
      'ROYAL_FLUSH': self.estimator.estimate_royal_flush_probability,
      'STRAIGHT_FLUSH': self.estimator.estimate_straight_probability,
      'FOUR_OF_A_KIND': self.estimator.estimate_four_kind_probability,
      'FULL_HOUSE': self.estimator.estimate_full_house_probability,
      'FLUSH': self.estimator.estimate_flush_probability,
      'STRAIGHT': self.estimator.estimate_straight_probability,
      'THREE_OF_A_KIND': self.estimator.estimate_three_kind_probability,
      'TWO_PAIR': self.estimator.estimate_two_pair_probability,
      'ONE_PAIR': self.estimator.estimate_one_pair_probability,
      'HIGH_CARD': self.estimator.estimate_high_card_probability
    }
  
  def decide(self,state):
    logger.info(f'{str(state.current_player)} Calculating....')
    hole = state.current_player.hand
    community = state.community_cards
    
    player_chips = state.current_player.chips
    winning_prob = self.calculate_winning_probability(hole,community)
    
    fold_EV = 0
    
    call_EV = self.calculate_call_EV(state,winning_prob)
    
    if state.num_raises == state.max_raises_round:
      logger.info("MAX RAISES REACHED ")
      raise_EV,raise_amt = -float('inf'),0
    else:
      raise_EV,raise_amt = self.calculate_raise_EV(state,winning_prob,player_chips)
    
    actions =[
      (fold_EV,"FOLD",0),
      (call_EV,"CALL",state.prev_bet),
      (raise_EV,"RAISE",raise_amt)
    ]
    
    logger.info(f'Hole: {[str(c) for c in hole]}, Community: {[str(c) for c in community]}')
    logger.info(f'Win Prob: {winning_prob:.4f}%')
    logger.info(f'Call EV: {call_EV}')
    logger.info(f'Raise EV: {raise_EV}, amt: {raise_amt}')
    best_ev, best_action, best_amount = max(actions, key=lambda x: x[0])
    return best_action, best_amount
  
  def calculate_call_EV(self,state,winning_prob):
    bet = state.prev_bet
    pot = state.pot
            
    hand_won = winning_prob*(pot+bet)
    hand_lost = (1-winning_prob) * -bet
    
    call_EV = hand_won + hand_lost
    return call_EV
  
  def calculate_raise_EV(self,state,winning_prob,player_chips):
    bet = state.prev_bet
    pot = state.pot
    active_players =  len([p for p in state.players if p.is_active])
        
    oppent_fold_prob = 0.25
    all_opponents_fold = oppent_fold_prob ** (active_players-1)
    
    candidate_raises = [b for b in range(5,pot,10)]
    
    raise_EV = -float('inf') 
    raise_amt = 0   
    for r in candidate_raises:
      new_bet = bet + r
      if new_bet > player_chips:
        break
      hand_won = winning_prob * (pot+new_bet)
      hand_lost = (1-winning_prob)*(-new_bet)
      curr_EV = all_opponents_fold*(pot+bet) + (1-all_opponents_fold)*(hand_won + hand_lost) 
      
      if curr_EV > raise_EV:
        raise_amt = r
        raise_EV = curr_EV
    
    return raise_EV,raise_amt
  
  def estimate_future_bets(self,active_players,current_player,bet):
    #estimates upcoming bets for current round and assumes remaining 
    #players will at least call or raise with prob .75
    
    future_bets = 0
    fold_probability = 0.25
    for p in active_players:
      if p.id == current_player.id:
        continue
      
      if p.chips <= 2*bet:
        fold_probability = 0.75
      
      future_bets += fold_probability*bet
    return future_bets
  
  
  def calculate_winning_probability(self,hole,community):
    #P(winning) = Summation of P(winning/rank_type)*P(rank_type)
    #P(winning/rank_type) - estimated using monte carlo of 500k hands
    total_winning_prob = 0
    
    
   # logger.info(f'Hole: {[str(c) for c in hole]}, Community: {[str(c) for c in community]}')
    for rank_type in self.rank_types:
      estimation_func = self.estimate_call_backs[rank_type]
      estimated_prob = estimation_func(hole=hole,community=community) #P(rank type)
      bayesian = self.bayesian_probabilities[rank_type] #P(winning/rank type)
      total_winning_prob += estimated_prob*bayesian
      #logger.info(f'Probability of {rank_type}: {estimated_prob*100:.4f}%')
    
    #logger.info(f'Total winning prob: {total_winning_prob*100:.4f}%')
    return total_winning_prob
    