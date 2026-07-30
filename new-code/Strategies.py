from abc import ABC, abstractmethod
from GameElements import GameState
import math
from collections import Counter
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
    
    winning_prob = self.calculate_winning_probability(hole,community)
    
    fold_EV = 0
    
    call_EV = self.calculate_call_EV(state,winning_prob)
    
    if state.num_raises == state.max_raises_round:
      logger.info("MAX RAISES REACHED ")
      raise_EV,raise_amt = -float('inf'),0
    else:
      raise_EV,raise_amt = self.calculate_raise_EV(state,winning_prob)
    
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
        
    #winning_prob = self.calculate_winning_probability(hole,community)
    
    hand_won = winning_prob*(pot+bet)
    hand_lost = (1-winning_prob) * -bet
    
    call_EV = hand_won + hand_lost
    return call_EV
  
  def calculate_raise_EV(self,state,winning_prob):
    bet = state.prev_bet
    pot = state.pot
    active_players =  len([p for p in state.players if p.is_active])
        
    oppent_fold_prob = 0.25
    all_opponents_fold = oppent_fold_prob ** active_players
    
    candidate_raises = [b for b in range(5,pot,10)]
    
    raise_EV = -float('inf') 
    raise_amt = 0   
    for r in candidate_raises:
      new_bet = bet + r
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
      logger.info(f'Probability of {rank_type}: {estimated_prob*100:.4f}%')
    
    #logger.info(f'Total winning prob: {total_winning_prob*100:.4f}%')
    return total_winning_prob
    
class ProbabilityEstimator():
  def __init__(self):
    self.suits = ['spades','clubs','heards','diamonds']
    self.all_straight_flushes = [{14,2,3,4,5}] + [set(range(i,i+5)) for i in range(2,10)]
    self.all_straights = [{14,2,3,4,5}] + [set(range(i,i+5)) for i in range(2,11)]
  
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
    
    royal_prob =  possible_ways/total_combinations
    
    return royal_prob
  
  def estimate_straight_flush_probability(self,hole,community):
    unknown_cards = 52 - (len(hole)+len(community))
    remaining_draws  = 5 - len(community)
    
    cards = hole+community
    favourable_outcomes = 0
    for suit in self.suits:
      same_suits = sorted([c.value for c in cards if c.suit == suit])
      possible_flush = []
      
      for flush in self.all_straight_flushes:
        missing = flush - set(same_suits)
        if len(missing) == 0:
          return 1
        
        if len(missing) <= remaining_draws:
          possible_flush.append(missing)
      
      for missing in possible_flush:
        required = len(missing)
        
        if required > remaining_draws:
          continue
        
        # num of cards remaining in deck after straight flush 
        # eg - 50 cards in deck (unknown) + 2 hole (1,2 diamonds), 
        # 3 cards req (3,4,5) to make flush, after which unused = 50-3 = 47
    
        unused_cards = unknown_cards - required
        
        # eg: hole (1,2), required = (3,4,5), draws remaining = 5,
        # filler cards = 5-3 = 2 
        filler_cards = remaining_draws - required
        favourable_outcomes += math.comb(unused_cards,filler_cards)
    
    print(favourable_outcomes)    
    total_outcomes = math.comb(unknown_cards,remaining_draws)
    
    return favourable_outcomes/total_outcomes
  
  def estimate_four_kind_probability(self,hole,community):
    unknown_cards = 52 - (len(hole)+len(community))
    remaining_draws = 5 - len(community)
    
    cards = hole+community
    rank_counts = Counter([c.value for c in cards])
    
    favourable_outcomes = 0
    for rank in range(2,15):
      count = rank_counts.get(rank,0)
      required = 4 - count
      if required == 0:
        return 1
      
      if required > remaining_draws:
        continue
      
      unused_cards = unknown_cards-required
      filler_cards = remaining_draws - required
      
      favourable_outcomes += math.comb(unused_cards,filler_cards)
    
    total_outcomes = math.comb(unknown_cards,remaining_draws)
    
    return favourable_outcomes/total_outcomes
  
  def estimate_full_house_probability(self,hole,community):
    unknown_cards = 52 - (len(hole)+len(community))
    remaining_draws = 5 - len(community)
    
    cards = hole+community
    rank_counts = Counter([c.value for c in cards])
    
    favourable_outcomes = 0
    
    #iterate over all possible full house combs, ie all triplet and double pairs
    for triplet in range(2,15):
      for pair in range(2,15):
        if pair == triplet:
          continue
        
        count1 = rank_counts.get(pair,0)
        required_to_form_pair = max(2 - count1,0)
        
        count2 = rank_counts.get(triplet,0)
        required_to_form_triplet = max(3- count2,0)
        
        required = required_to_form_pair + required_to_form_triplet
        
        if required == 0:
          return 1
        
        if required > remaining_draws:
          continue
        
        unused_cards = unknown_cards - required
        filler_cards = remaining_draws - required
        
        favourable_outcomes += math.comb(unused_cards,filler_cards)
    
    total_outcomes = math.comb(unknown_cards,remaining_draws)
    
    return favourable_outcomes/total_outcomes
  
  def estimate_flush_probability(self,hole,community):
    unknown_cards = 52 - (len(hole)+len(community))
    remaining_draws = 5 - len(community)
    cards = hole+community
    
    favourable_outcomes = 0
    for suit in self.suits:
      same_suit = [c.value for c in cards if c.suit==suit]
      required = 5 - len(same_suit)
      
      if required <=0:
        return 1
      
      if required > remaining_draws:
        continue
      
      remaining_suit_cards = 13 - len(same_suit)
      suit_combos = math.comb(remaining_suit_cards,required)
      
      max_possible = min(remaining_suit_cards,remaining_draws)
      for k in range(required,max_possible+1):
        unused_cards = unknown_cards - remaining_suit_cards
        filler_cards = remaining_draws - k
        suit_combos = math.comb(remaining_suit_cards,k)
        favourable_outcomes += suit_combos * math.comb(unused_cards,filler_cards)
    
    total_outcomes = math.comb(unknown_cards,remaining_draws)
    
    return favourable_outcomes/total_outcomes
  
  def estimate_straight_probability(self,hole,community):
    unknown_cards = 52 - (len(hole)+len(community))
    remaining_draws  = 5 - len(community)
        
    cards = hole+community
    favourable_outcomes = 0
    
    s = set([c.value for c in cards])
    possible_straights = []
    for straight in self.all_straights:
      missing = straight - s
      if len(missing) == 0:
        return 1
      
      if len(missing) <= remaining_draws:
        possible_straights.append(straight)
    
    for missing in possible_straights:
      required = len(missing)
      
      if required > remaining_draws:
        continue
      
      unused_cards = unknown_cards-required
      filler_cards = remaining_draws-required
      favourable_outcomes += (4**required)*math.comb(unused_cards,filler_cards)
    
    total_outcomes = math.comb(unknown_cards,remaining_draws)
    
    return favourable_outcomes/total_outcomes
  
  def estimate_three_kind_probability(self,hole,community):
    unknown_cards = 52 - (len(hole)+len(community))
    remaining_draws = 5 - len(community)
    
    cards = hole+community
    rank_counts = Counter([c.value for c in cards])
    
    favourable_outcomes = 0
    for rank in range(2,15):
      count = rank_counts.get(rank,0)
      required = 3 - count
      if required <= 0:
        return 1
      
      if required > remaining_draws:
        continue
      
      unused_cards = unknown_cards-required
      filler_cards = remaining_draws - required
      
      favourable_outcomes += math.comb(4-count,required)*math.comb(unused_cards,filler_cards)
    
    total_outcomes = math.comb(unknown_cards,remaining_draws)
    
    return favourable_outcomes/total_outcomes

  def estimate_two_pair_probability(self,hole,community):
    unknown_cards = 52 - (len(hole)+len(community))
    remaining_draws = 5 - len(community)
    
    cards = hole+community
    rank_counts = Counter([c.value for c in cards])
    
    favourable_outcomes = 0
    
    for pair1 in range(2,15):
      for pair2 in range(pair1,15):
        if pair1 == pair2:
          count = rank_counts.get(pair1,0)
          c1 = 2 if count>=2 else count
          c2 = count - c1
        else:
          c1 = rank_counts.get(pair1,0)
          c2 = rank_counts.get(pair2,0)
        
        r1 = max(2-c1,0)
        r2 = max(2-c2,0)
        required = r1+r2
        if required <= 0:
          return 1
        
        if required > remaining_draws:
          continue
        
        unused_cards = unknown_cards - required
        filler_cards = remaining_draws - required
        favourable_outcomes += math.comb(4-c1,r1)*math.comb(4-c2,r2)*math.comb(unused_cards,filler_cards)
    
    total_outcomes = math.comb(unknown_cards,remaining_draws)
    
    return favourable_outcomes/total_outcomes
        
  def estimate_one_pair_probability(self,hole,community):
    unknown_cards = 52 - (len(hole)+len(community))
    remaining_draws = 5 - len(community)
    
    cards = hole+community
    rank_counts = Counter([c.value for c in cards])
    
    favourable_outcomes = 0
    for rank in range(2,15):
      count = rank_counts.get(rank,0)
      required = 2 - count
      if required <= 0:
        return 1
      
      if required > remaining_draws:
        continue
      
      unused_cards = unknown_cards-required
      filler_cards = remaining_draws - required
      
      favourable_outcomes += math.comb(4-count,required)* math.comb(unused_cards,filler_cards)
    
    total_outcomes = math.comb(unknown_cards,remaining_draws)
    
    return favourable_outcomes/total_outcomes
  
  def estimate_high_card_probability(self,hole,community):
    return 1