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
