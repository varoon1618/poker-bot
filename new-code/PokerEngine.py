from itertools import product
import random
import logging
from GameElements import Card,Deck,Player,GameState
from BotController import BotController
from Evaluators import HandRank,HandEvaluator

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class PokerEngine:
  '''TODO: Add logging
  HANDLING CONTINUOUS GAMES WHEN PLAYERS FOLD
  WHEN A PERSON CALLS, BUT BET > CHIPS HANDLE THAT
  MAXIMUM AMOUNT TO RAISE
  '''
  def __init__(self):
    self.listeners = []
    self.pot = 0
    self.players = []
    self.add_players()
    self.community_cards = []
    self.deck = None
    self.current_player_idx = 0
    self.round = None
    self.has_acted = set() #set of players that have already acted this round
    self.num_raises = 0
    self.MAX_RAISES_ROUND = 2 #max raises PER ROUND
    self.prev_bet = 5
    self.bot_controller = BotController()
    self.exception = None
    self.new_round = None
    self.winners = []
    self.game_complete = False
    self.winning_rank_name = None
    self.can_continue_game = None
    self.can_continue_betting = None
    self.human_id = 0
  
  def register_listener(self,callback):
    self.listeners.append(callback)
  
  def _broadcast_state(self):
    for callback in self.listeners:
      callback(self.get_game_state())
  
  def get_game_state(self):
    
    current_state = GameState.from_game_engine(self)
    return current_state
    
  def add_players(self):
    bot1 =  Player(id=1,is_human=False)
    self.players.append(bot1)
    
    bot2 = Player(id=2,is_human=False)
    self.players.append(bot2)
    
    human = Player(id=0,is_human=True)
    self.players.append(human)
    
    bot3 = Player(id=3,is_human=False)
    self.players.append(bot3)
    
    bot4 = Player(id=4,is_human=False)
    self.players.append(bot4)
      
  def initialise_game(self):
    #reset deck
    self.deck = Deck()
    self.deck.shuffle()
    
    #reset community attrs
    self.community_cards = []
    self.pot = 0
    self.can_continue_game = True
    self.can_continue_betting = True
    
    #reset player attrs
    non_bust_players = [p for p in self.players if p.chips>5]
    
    ids = [p.id for p in non_bust_players]
    if self.human_id not in ids:
      self.can_continue_game = False
      logger.info("Went Bust")
      self.exception = 'Game Over: You went bust, Please Restart'
      self._broadcast_state()
      return
    
    if len(ids) == 1:
      self.can_continue_game = False
      self.exception = 'No other players remaining, please restart'
      self._broadcast_state()
      return
    
    for p in self.players:
      p.hand = []
      p.latest_action = None
      p.current_bet = 0
      p.has_folded = False
      p.is_all_in = False
      
      if p.chips < 5:
        p.latest_action = 'BUST'
        p.has_folded = True
        
    #reset game state
    self.round = "BUY_IN"
    self.has_acted = set() #set of players that have already acted this round
    self.num_raises = 0
    self.current_player_idx = 0
    self.prev_bet = 5
    self.exception = None
    self.new_round = None
    self.winners = []
    self.game_complete = False
    self.winning_rank_name = None

    self._broadcast_state()
  
  def _get_next_active_player_idx(self, start_index=None):
    if start_index is None:
        start_index = self.current_player_idx
    
    num_players = len(self.players)
    
    for i in range(1, num_players + 1):
        idx = (start_index + i) % num_players
        player = self.players[idx]
        
        if not player.has_folded and not player.is_all_in:
            return idx 
    
    return None
  
  def _get_first_actor_idx(self):
    bot1 = self.players[0]
    if bot1.is_active:
      return 0
    
    return self._get_next_active_player_idx(start_index=0)
  
  def _check_round_over(self):
    active_players = [p for p in self.players if p.is_active]
    
    if len(active_players) <1:
      return True
    
    for p in active_players:
      if p not in self.has_acted:
        return False
    
    return True

  
  def _check_all_folded(self):
    not_folded = [p for p in self.players if not(p.has_folded)]
    return len(not_folded) == 1
  
  def _check_everybody_all_in(self):
    not_folded = [p for p in self.players if not(p.has_folded)]
    return all(p.is_all_in for p in not_folded)
  
  def _advance_round(self):     
    if self.round == 'BUY_IN':
      self.round = 'PREFLOP'
      for p in self.players:
        if p.chips < self.prev_bet:
          continue
        hand = self.deck.deal_cards(2)
        p.update_hand(hand)
      
    elif self.round == 'PREFLOP':
      self.round = 'FLOP'
      flop = self.deck.deal_cards(3)
      self.community_cards.extend(flop)
    
    elif self.round == 'FLOP':
      self.round = 'TURN'
      turn = self.deck.deal_cards(1)
      self.community_cards.extend(turn)
    
    elif self.round == 'TURN':
      self.round = 'RIVER'
      river = self.deck.deal_cards(1)
      self.community_cards.extend(river)
    
    elif self.round == 'RIVER':
      if not(self._check_all_folded()):
        self.round = 'SHOWDOWN'  
      
      self.winners,self.winning_rank_name = self._calculate_winners()
      self.game_complete = True
      self._update_winnings(self.winners)      
      self._broadcast_state()
      return
    
    # all active players and bots are all in no further interactive actions
    if self._check_everybody_all_in():
      self.can_continue_betting = False
      logger.info("EVERBODY ALL IN: ADVANCE ROUND")
      self._broadcast_state()
      return

    self.has_acted = set()
    self.prev_bet = 5
    self.num_raises = 0
    self.exception = None
    self.current_player_idx = self._get_first_actor_idx() 
    self._broadcast_state()
    
    for p in self.players:
      p.latest_action =  None if not(p.has_folded) else 'FOLD'
  
  
  def _update_winnings(self,winners):
    winnings = self.pot // len(self.winners)
    for w in winners:
      w.chips += winnings
  
  def handle_action(self,action,amount=0):
    '''
    TODO: Add additional check for is game over
    '''
    self.exception = None
    self.new_round = False
    
    curr_player = self.players[self.current_player_idx]
    
    if self.round == 'BUY_IN':
      try:
        self.handle_buy_in(curr_player)
        logger.info(f'{curr_player} bought in successfully')
      except ValueError as e:
        logger.info(f'Exception by {curr_player}: {e}')
        self.exception = e
        self._broadcast_state()
        return
      
    elif action == 'CALL':
      try:
        self.handle_call(curr_player)
        logger.info(f'{curr_player} called successfully')
      except ValueError as e:
        logger.info(f'Exception by {curr_player}: {e}')
        self.exception = e
        self._broadcast_state()
        return
          
    elif action == 'RAISE':
      try:
        self.handle_raise(curr_player,amount)
        logger.info(f'{curr_player} raised {amount}')
      
      except ValueError as e:
        self.exception = e
        self._broadcast_state()
        return
    
    elif action == 'FOLD':
      try:
        self.handle_fold(curr_player)
        
      except ValueError as e:
        self.exception = e
        self._broadcast_state()
        return
    
    self.has_acted.add(curr_player)
    next_idx = self._get_next_active_player_idx()
    self.current_player_idx = 0 if next_idx is None else next_idx
    
    if self._check_all_folded():
      self.winners,self.winning_rank_name = self._calculate_winners()
      self.game_complete = True
      self._update_winnings(self.winners)
      self._broadcast_state()
      return
    
    if self._check_everybody_all_in():
      logger.info("EVERBODY ALL IN")
      self.can_continue_betting = False
      self._broadcast_state()
      return
    
    if self._check_round_over():
      self.new_round = True
      self._advance_round()
    else:
      self._broadcast_state()
    
  
  def _calculate_winners(self):
    winners = []
    highest_rank = None
    not_folded = [p for p in self.players if not(p.has_folded)]
    if len(not_folded) == 1:
      winners.append(not_folded[0])
      logger.info(f'Winner is :{winners}, all others folded')
      return winners,None
    
    logger.info(f'Community cards: {[str(c) for c in self.community_cards]}')
    for p in not_folded:
      hand_rank = HandEvaluator.rank_cards(hole=p.hand,community=self.community_cards)
      p.hand_rank = hand_rank
      logger.info(f'{p}\'s hole: {[str(c) for c in p.hand]}, handrank: {hand_rank.rank_name}')
      if highest_rank is None or hand_rank > highest_rank:
        highest_rank = hand_rank
        winners = [p]
      
      elif hand_rank == highest_rank:
        winners.append(p)
      
    logger.info(f'Winner is :{winners}, with rank: {highest_rank.rank_name}')  
    return winners,highest_rank.rank_name
  
  def bot_action(self):
    curr_player = self.players[self.current_player_idx]
    if curr_player.is_human:
      raise RuntimeError("Current Player human, bot method called")
    
  def handle_buy_in(self,player):
    if player.chips < self.prev_bet:
      player.latest_action = 'BUST'
      player.has_folded = True
      self._broadcast_state()
      return
      
    player.chips -= self.prev_bet
    self.pot += self.prev_bet
    player.latest_action = 'BUY_IN'
    player.current_bet = self.prev_bet
    return
  
  def handle_call(self,player):
    bet = self.prev_bet
    if player.chips == 0:
      player.is_all_in = True
      return
    if player.chips <= self.prev_bet:
      player.is_all_in = True
      bet = player.chips
      
    player.chips -= bet
    self.pot += bet
    player.latest_action = 'CALL'
    player.current_bet = self.prev_bet
    return
      
  
  def handle_raise(self,player,amount):
    if not(isinstance(amount,int)) or amount <= 0:
      raise ValueError("Enter a positive integer")
    
    if self.num_raises >= self.MAX_RAISES_ROUND:
      raise ValueError(f"Cannot raise more than {self.MAX_RAISES_ROUND} times per round")
    
    if player.chips <amount:
      raise ValueError("Too few chips")
    
    if player.chips == amount:
      player.is_all_in = True
    
    self.prev_bet += amount
    self.pot += amount
    
    player.chips -= amount
    player.latest_action = 'RAISE'
    player.current_bet = amount
    
    if self.num_raises < self.MAX_RAISES_ROUND:
      self.num_raises +=1
      self.has_acted = set()
      
    return
  
  def handle_fold(self,player):
    if player.has_folded:
      raise ValueError("already folded")
    
    player.latest_action = 'FOLD'
    player.has_folded = True
    logger.info(f'{str(player)} Folded')
    return
  
      
    