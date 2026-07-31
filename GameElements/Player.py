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
    self.hand_rank = None
  
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
