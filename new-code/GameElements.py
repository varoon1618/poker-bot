import random
from itertools import product

class Card:
  def __init__(self,suit,value):
    self.suit = suit
    self.value = value
    self.unicodes = {"spades":"\u2660","hearts":'\u2665',"clubs":'\u2663',"diamonds":'\u2666'}
  
  def __repr__(self):
    return f'Card({self.value},{self.suit})'
  
  def __str__(self):
    s = self.unicodes.get(self.suit)
    if s is None:
      raise ValueError("suit unicode not found")
  
    return f'{self.value}{s}'
    
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
    self.latest_action = None
  
  def __repr__(self):
    return f'Player(id={self.id},chips={self.chips})'
  
  def __str__(self):
    if self.is_human:
      return 'Human'
    
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

