from abc import ABC, abstractmethod
from GameElements import GameState
import math
class BotStrategy(ABC):
  @abstractmethod
  def decide(self,state:GameState):
    '''Takes in Gamestate, and returns 
    Action (CALL,FOLD,RAISE), with optional AMOUNT'''
    pass

class CombinatorialStrategy(BotStrategy):
  def decide(self,state):
    return "CALL",10

class ProbabilityEstimator():
  def __init__(self):
    self.suits = ['spades','clubs','heards','diamonds']
    self.all_straight_flushes = [{14,2,3,4,5}] + [set(range(i,i+5)) for i in range(2,10)]
  
  def estimate_royal_flush_probability(self,hole,community):
    all_cards = hole+community
    
    royal_values = {14,13,12,11,10}
    remaining_draws = 5 - (len(community))
    
    best_count = 0
    royal_candidate_suits = []
    
    for suit in self.suits:
      #get all cards with same suit, and 'royal' values
      suit_royals = [c for c in all_cards if c.suit==suit and c.value in royal_values]
      count = len(suit_royals)
      
      #choose suit with best odds of creating a royal flush
      if count > best_count:
        best_count = count
        royal_candidate_suits = [suit]
      
      #could be multiple suits with eq prob (Eg: A,K hearts, A,K spades, draws remaining = 3)
      if count == best_count:
        royal_candidate_suits.append(suit)
      
    required = 5 - best_count
    
    if required == 0:
      return 1
    
    if required > remaining_draws:
      return 0
    
    deck_cards = 52 - (len(community)+len(hole))
    
    # no of cards remaining in deck choose remaining draws
    total_combinations = math.comb(deck_cards,remaining_draws)
    
    # Eg: K hearts, K spades, draws remaining = 5, required cards = 4 (for each suit)
    # possible ways = 46 for each suit (4 spots are locked in, now 52-4-2=46 cards available fo
    # 5th spot)
    # ie num_suits * (remaining_cards choose filler cards) 
    
    filler_spots = remaining_draws-required
    remaining_cards = deck_cards-required
    possible_ways = math.comb(remaining_cards,filler_spots)*len(royal_candidate_suits)
    
    print(f'possible: {possible_ways}, total: {total_combinations}')
    royal_prob =  possible_ways/total_combinations
    
    return royal_prob
  
  def estimate_straight_flush_probability(self,hole,community):
    deck_cards = 52 - (len(hole)+len(community))
    remaining_draws  = 5 - len(community)
    
    cards = hole+community
    possible_ways = 0
    for suit in self.suits:
      same_suits = sorted([c.value for c in cards if c.suit == suit])
      possible_flush = []
      
      for flush in self.all_straight_flushes:
        missing = flush - set(same_suits)
        #print(f'suit: {suit}, flush:{flush}, current_cards: {same_suits}, missing: {missing}')
        if len(missing) <= remaining_draws:
          possible_flush.append(missing)
      
      for missing in possible_flush:
        required = len(missing)
        remaining_cards = deck_cards - required
        filler_cards = remaining_draws-required
        possible_ways += math.comb(remaining_cards,filler_cards)
        #print(f'missing: {missing}, ways: {possible_ways}, draws_remaining: {remaining_draws}')
    
    print(possible_ways)    
    total_possibilities = math.comb(deck_cards,remaining_draws)
    
    return possible_ways/total_possibilities
  
  