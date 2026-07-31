import random
from .Card import Card
from itertools import product

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
