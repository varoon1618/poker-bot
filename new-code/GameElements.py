import random
from itertools import product

class Card:
  def __init__(self,suit,value):
    self.suit = suit
    self.value = value
    self.unicodes = {"spades":"\u2660","hearts":'\u2665',"clubs":'\u2663',"diamonds":'\u2666'}
    self.str_rep = {14:'A',11:'J',12:'Q',13:'K'}
  
  def __repr__(self):
    return f'Card({self.value},{self.suit})'
  
  def __str__(self):
    s = self.unicodes.get(self.suit)
    if s is None:
      raise ValueError("suit unicode not found")
    
    v = self.str_rep.get(self.value,self.value)
    return f'{v}{s}'
  
  def __eq__(self,other):
    if not(isinstance(other,Card)):
      return False
    
    return self.value == other.value
  
  def __lt__(self,other):
    if not(isinstance(other,Card)):
      raise ValueError(f"cannot compare card to {type(other)}")
    return self.value < other.value
  
class Deck:
  def __init__(self):
    self.suits = ['spades','hearts','diamonds','clubs']
    self.values = range(2,15)
    self.cards = [Card(suit=s,value=v) for s,v in product(self.suits,self.values)]
  
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
  
  def _generate_royal_flush(self):
    out = []
    values = [14,13,12,11,10]
    suit = random.choice(self.suits)
    
    for v in values:
      out.append(Card(suit=suit,value=v))
    return out
  
  def _generate_straight_flush(self):
    out = []
    low = random.randint(2,9)
    values = [low+i for i in range(5)]
    suit = random.choice(self.suits)
    for v in values:
      out.append(Card(suit=suit,value=v))
    
    return out 
    
  def _generate_four_kind_hand(self):
    out = []
    v = random.randint(2,14)
    for i  in range(4):
      suit = self.suits[i]
      out.append(Card(suit=suit,value=v))
    
    out.append(Card(suit=suit,value=v+1))
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
    self.latest_action = None
  
  def __repr__(self):
    return f'Player(id={self.id},chips={self.chips})'
  
  def __str__(self):
    if self.is_human:
      return 'You'
    
    return f'Bot{self.id}'
  
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
    self.players = kwargs.get('players',[])
    self.num_raises = kwargs.get('num_raises',0)
    self.exception = kwargs.get('exception',None)
    self.new_round = kwargs.get('new_round',False)
    self.winners = kwargs.get('winners',None)
    self.game_complete = kwargs.get('game_complete',False)
    self.winning_rank_name = kwargs.get('winning_rank_name',None)
  
  @classmethod
  def from_game_engine(cls,engine):
    current_player = engine.players[engine.current_player_idx]
    players = engine.players
    pot = engine.pot
    community_cards = engine.community_cards
    round = engine.round
    prev_bet = engine.prev_bet
    num_raises = engine.num_raises
    exception = engine.exception
    new_round = engine.new_round
    winners = engine.winners
    game_complete = engine.game_complete
    winning_rank_name = engine.winning_rank_name
    
    return cls(current_player=current_player,pot=pot,community_cards=community_cards,
               round = round, prev_bet=prev_bet,players = players, num_raises=num_raises,
               exception = exception,new_round=new_round,winners=winners,
               game_complete=game_complete, winning_rank_name=winning_rank_name)

