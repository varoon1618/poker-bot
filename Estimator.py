class Estimator:
  hand = []
  community = []
  
  def returnBestMove(self,player):
    self.hand = player.hand
    self.community = player.communityCards
  
  def royalFlushProbability(self,player):
    
    if not self.isSameSuit(self,player):
      return 0
    
    
  def isSameSuit(self, player):
    cards = player.hand + self.communityCards
    suits = [card[0] for card in cards]
    first_suit = suits[0]
    return all(suit == first_suit for suit in suits)
  
  def isConsecutive(self,player):
    cards =  player.hand + self.communityCards
    values = [int(c[1:]) for c in cards]
    values.sort()
    for i in range(len(values) - 1):
      if values[i + 1] != values[i] + 1:
        return False
    return True
  
  def isSameValue(self,player):
    cards = player.hand+ self.communityCards
    values = [int(c[1:]) for c in cards]
    for i in range(len(values)-1):
      if values[i+1] != values[i]:
        return False
      return True
  
  def returnPairs(self,player):
    cards = player.hand+self.communityCards
    values = [int(c[1:]) for c in cards]
    counts = [values.count(v) for v in values]
    return int(counts.count(2)/2)
  
  def returnTriplets(self,player):
    cards = player.hand+self.communityCards
    values = [int(c[1:]) for c in cards]
    counts = [values.count(v) for v in values]
    return int(counts.count(3)/3)
  
  def isRoyalFlush(self,player):
    cards = player.hand+ self.communityCards
    values = [int(c[1:]) for c in cards]
    return set(values) == {1,10,11,12,13} and self.isSameSuit(cards)
  
    
    