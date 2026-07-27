from itertools import product
import random
import logging
from GameElements import Card,Deck,Player,GameState
from BotController import BotController

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class PokerEngine:
  '''TODO: Add logging'''
  def __init__(self):
    self.listeners = []
    self.pot = 0
    self.players = []
    self.community_cards = []
    self.deck = Deck()
    self.current_player_idx = 0
    self.round = None
    self.has_acted = set() #set of players that have already acted this round
    self.num_raises = 0
    self.MAX_RAISES_ROUND = 2 #max raises PER ROUND
    self.prev_bet = 5
    self.bot_controller = BotController()
    self.exception = None
  
  def register_listener(self,callback):
    self.listeners.append(callback)
  
  def _broadcast_state(self):
    for callback in self.listeners:
      callback(self.get_game_state())
  
  def get_game_state(self):
    '''TODO: ADD more attrs to game state'''
    
    current_state = GameState.from_game_engine(self)
    return current_state
    
  def add_players(self):
    human = Player(id=0,is_human=True)
    self.players.append(human)
    
    for i in range(1,5):
      bot = Player(id=i,is_human=False)
      self.players.append(bot)
  
  def initialise_game(self):
    self.add_players()
    
    self.deck.shuffle()
    for p in self.players:
      hand = self.deck.deal_cards(2)
      p.update_hand(hand)
    
    self.round = "PREFLOP"
    
    self.current_player_idx = 0
    
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
    human = self.players[0]
    if human.is_active:
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

  
  def _check_is_game_over(self):
    '''
    TODO: ADD OTHER CHECKS FOR GAME END 
    LIKE - LAST ROUND, EVERYONE IS ALL IN ETC
    '''
    pass  
  
  def _advance_round(self):
    '''
    TODO: Add logic for post river rounds
    '''
    
    if self.round == 'PREFLOP':
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
      pass
    
    self.has_acted = set()
    self.prev_bet = 0
    self.current_player_idx = self._get_first_actor_idx()
    self._broadcast_state()
  
  def handle_action(self,action,amount=0):
    '''
    TODO: Add additional check for is game over
          Validation of input action
    '''
    self.exception = None
    curr_player = self.players[self.current_player_idx]
    
    if action == 'CALL':
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
    self.current_player_idx = self._get_next_active_player_idx()
    
    if self._check_round_over():
      self._advance_round()
    else:
      self._broadcast_state()
    
  
  def bot_action(self):
    curr_player = self.players[self.current_player_idx]
    if curr_player.is_human:
      raise RuntimeError("Current Player human, bot method called")
    
    
  def handle_call(self,player):
      if player.chips < self.prev_bet:
        raise ValueError("Too few chips")
      
      player.chips -= self.prev_bet
      self.pot += self.prev_bet
      player.latest_action = 'CALL'
      player.current_bet = self.prev_bet
      return
      
  
  def handle_raise(self,player,amount):
    if player.chips < amount:
      raise ValueError("Too few chips")
    
    if self.num_raises > self.MAX_RAISES_ROUND:
      raise ValueError(f"cannot raise more than {self.MAX_RAISES_ROUND} times per round")
    
    self.prev_bet = amount
    self.pot += amount
    
    player.chips -= amount
    player.latest_action = 'RAISE'
    player.current_bet = amount
    
    if self.num_raises < self.MAX_RAISES_ROUND:
      self.num_raises +=1
      self.has_acted = set()
      
    return
  
  def handle_fold(self,player):
    
    if not(player.has_folded):
      raise ValueError("already folded")
    
    player.latest_action = 'FOLD'
    player.has_folded = True
    return
  
      
    