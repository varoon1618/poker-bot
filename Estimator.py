import math

class Estimator:
  hand = []
  community = []
  
  def returnBestMove(self,player):
    self.hand = player.hand
    self.community = player.communityCards
  
  def royalFlushProbability(self,player):
    
    if not self.isPossibleRoyalFlush():
      return 0
    
    cards = self.hand + self.community
    royalFlushValues = {1,10,11,12,13}
    cardValues = self.returnValues(cards)
    common = set(cardValues) & royalFlushValues
    requiredCards = 5 - len(common) #cards required to complete royal flush
    remainingCards = 52 - (len(self.community) + 2*5) # cards that have not been dealt
    drawsLeft = 5 - len(self.community)
    playerSuits = self.returnSuits(self.hand)
    
    if len(set(playerSuits)) == 1:
      totalCombinations = math.comb(remainingCards,drawsLeft)
      optimalCombinations = math.comb(remainingCards - requiredCards, drawsLeft - requiredCards)
      return optimalCombinations/totalCombinations
    
    if len(set(playerSuits)) == 2:
      print("TO DO")
      
    cards = self.hand + self.community
    
    remainingCards = 52 - (len(self.community) + 2*5)
    drawsLeft = 5- len(self.community) #no of community cards left to draw
    totalCombinations = math.comb(remainingCards,drawsLeft)
    return (1/totalCombinations) # only one way to get royal flush of a given suit
  
  
  def isPossibleRoyalFlush(self):
    cards = self.hand + self.community
    flushValues = {1,10,11,12,13}
    remainingDraws = 5-len(self.community)
    suitCounts = {}
    
    for card in cards:
      suit = card[0]
      value = int(card[1:])
      if value in flushValues:
        suitCounts[suit] = suitCounts.get(suit,0)+1
    
    requiredCards = 5 - max(suitCounts.values())

    if not suitCounts:
      return False
        
    if requiredCards > remainingDraws:
      return False
    
    return True
    
    
    
    
    
    
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
  
  def returnValues(cards):
    return [int(c[1:]) for c in cards]
  
  def returnSuits(cards):
    return [c[0] for c in cards]
    
    