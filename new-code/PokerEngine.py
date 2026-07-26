from itertools import product
import random
import logging

logger = logging.getLogger(__name__)
class Card:
  def __init__(self,suit,value):
    self.suit = suit
    self.value = value
  
  def __repr__(self):
    return f'Card({self.value},{self.suit})'

class Deck:
  def __init__(self):
    suits = ['spades','hearts','diamonds','clubs']
    values = range(1,14)
    self.cards = [Card(suit=s,value=v) for s,v in product(suits,values)]
  
  def shuffle(self):
    random.shuffle(self.cards)
    return
  
  def draw(self):
    if not self.cards:
      raise ValueError("Deck is Empty")
    return self.cards.pop()
  
  def deal_cards(self,n):
    out = []
    for _ in range(n):
      out.append(self.draw())
    return out
    
class Player:
  def __init__(self,id,is_human):
    self.hand = []
    self.id = id
    self.is_human = is_human
    self.chips = 1000
    self.current_bet = 0
    self.has_folded = False
    self.is_all_in = False
  
  def update_hand(self,cards):
    self.hand.extend(cards)
    return
  
  def fold(self):
    self.has_folded = True
  
  @property
  def is_active(self):
    return not(self.has_folded) and not(self.is_all_in)

class GameState:
  def __init__(self,**kwargs):
    self.pot = kwargs.get('pot',0)
    self.current_player = kwargs.get('current_player')
    self.round = kwargs.get('round')
    self.community_cards = kwargs.get('community_cards',[])
    self.prev_bet = kwargs.get('prev_bet',0)
    self.current_player_action = kwargs.get('current_player_action')
    self.players = kwargs.get('players',[])
    
  
  @classmethod
  def from_game_engine(cls,engine):
    current_player = engine.players[engine.current_player_idx]
    pot = engine.pot
    community_cards = engine.community_cards
    round = engine.round
    prev_bet = engine.prev_bet
    current_player_action = engine.current_player_action
    
    return cls(current_player=current_player,pot=pot,community_cards=community_cards,
               round = round, prev_bet=prev_bet,current_player_action=current_player_action,
               players = engine.players)
    
  
class PokerEngine:
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
    self.prev_bet = 0
    self.current_player_action = None
    
  
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
    if human.is_active():
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
    
    self.has_acted = {}
    self.prev_bet = 0
    self.current_player_idx = self._get_first_actor_idx()
    self._broadcast_state()
  
  def handle_action(self,action,amount=0):
    '''
    TODO: Add additional check for is game over
          Validation of input action
          individual handle methods
    '''
    curr_player = self.players[self.current_player_idx]
    
    if action == 'CALL':
      try:
        self.handle_call(curr_player)
      except ValueError as e:
        #Add log statement
        self._broadcast_state()
        return
          
    if action == 'RAISE':
      try:
        self.handle_raise(curr_player,amount)    
      except ValueError as e:
        self._broadcast_state()
        return
    
    if action == 'FOLD':
      try:
        self.handle_fold(curr_player)
      except ValueError as e:
        self._broadcast_state()
        return
    
    self.has_acted.add(curr_player)
    
    self.current_player_idx = self._get_next_active_player_idx()
    
    if self._check_round_over():
      self._advance_round()
    else:
      self._broadcast_state()
  
  def handle_call(self,player):
      if player.chips < self.prev_bet:
        raise ValueError("Too few chips")
      
      player.chips -= self.prev_bet
      self.pot += self.prev_bet
      return
      
  
  def handle_raise(self,player,amount):
    if player.chips < amount:
      raise ValueError("Too few chips")
    
    player.chips -= amount
    self.prev_bet = amount
    self.pot += amount
    
    if self.num_raises < self.MAX_RAISES_ROUND:
      self.num_raises +=1
      self.has_acted = set()
    
    return
  
  def handle_fold(self,player):
    
    if not(player.has_folded):
      raise ValueError("Player already folded")
    
    player.has_folded = True
    return
  
      
    