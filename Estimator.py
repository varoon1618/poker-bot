import math

class Estimator:
  hand = []
  community = []
  
  def returnBestMove(self,player):
    self.hand = player.hand
    self.community = player.communityCards
  
  def royalFlushProbability(self):
    
    #to do - account for probability of royal flush cards not in opponents hand
    
    flushValues ={1,10,11,12,13}
    remainingDraws = 5 - len(self.community)
    playerValues = [int(c[1:]) for c in self.hand]
    playerSuits = [c[0] for c in self.hand]
    probability = 0
    remainingCards = 52 -(2*5 + len(self.community))
    
    if not set(playerValues) & flushValues:
      return 0
    
    
    for suit in set(playerSuits):
      playerRoyal = [int(c[1:]) for c in self.hand if 
                     c[0] == suit and int(c[1:]) in flushValues]
      
      communityRoyal = [int(c[1:]) for c in self.community if 
                        c[0] == suit and int(c[1:]) in flushValues]
      
      requiredRoyal = 5 - (len(playerRoyal) + len(communityRoyal))
      
      if requiredRoyal == 0:
        probaility +=  1
      
      if requiredRoyal <= remainingDraws:
        totalCombinations = math.comb(remainingCards,remainingDraws)
        optimalCombinations = math.comb(remainingCards-requiredRoyal, remainingDraws - requiredRoyal)
        probability += optimalCombinations/totalCombinations
        
    return probability
  
  def straightFlushProbability(self):
    probability = 0
    remainingDraws = 5 - len(self.community)
    remainingCards = 52 - (2*5 + len(self.community))  # 2*5: 5 players, 2 cards each

    suits_in_hand = set([c[0] for c in self.hand])
    for suit in suits_in_hand:
        # Get all cards of this suit in hand and community
        suited_cards = [int(c[1:]) for c in self.hand + self.community if c[0] == suit]
        suited_cards = sorted(set(suited_cards))

        # Check for possible straight flushes (A can be high or low)
        possible_straights = []
        for start in range(1, 11):  # 1 to 10 (A-5 to 10-K)
            straight = set(range(start, start+5))
            # Special case for A-5 straight
            if start == 1 and 14 not in suited_cards and 1 in suited_cards:
                straight = {1, 2, 3, 4, 5}
            missing = straight - set(suited_cards)
            if len(missing) <= remainingDraws:
                possible_straights.append(missing)

        # For each possible straight flush, calculate probability
        for missing in possible_straights:
            required = len(missing)
            if required == 0:
                # Already have straight flush
                probability += 1
            elif required <= remainingDraws:
                totalCombinations = math.comb(remainingCards, remainingDraws)
                optimalCombinations = math.comb(remainingCards - required, remainingDraws - required)
                probability += optimalCombinations / totalCombinations

    return probability      
  
  def returnConsecutive(self, player):
    cards = player.hand + self.communityCards
    vals = [int(c[1:]) for c in cards]
    uniq = sorted(set(vals))
    if 1 in uniq:
      uniq.append(14)
    
    count = max_count = 1
    for i in range(1, len(uniq)):
      if uniq[i] == uniq[i-1] + 1:
          count += 1
          max_count = max(max_count, count)
      else:
          count = 1

    return max_count 
  
  def isSameSuit(cards):
    suits = [card[0] for card in cards]
    first_suit = suits[0]
    return all(suit == first_suit for suit in suits)
  
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
    
    