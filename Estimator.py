import math
from collections import Counter

class Estimator:
  hand = []
  community = []
  pot = -1
  
  def returnBestMove(self,player,pot,previousBet):
    self.hand = player.hand
    self.community = player.communityCards
    self.pot = pot 
    probability = self.calculateFinalProbability()
    expectedValue = probability*pot
    drawsLeft = 5-len(self.community)
    if expectedValue > 2*previousBet:
      bet = min(player.money/max(1,drawsLeft),2*previousBet)
      action = "raise"
    elif expectedValue > previousBet:
      bet = previousBet
      action = "call"
    else:
      bet = 0
      action = "fold"
    
    return {"action":action,"bet":bet,"expectedValue":expectedValue,"proability":probability}
    
      
    
  def calculateFinalProbability(self):
    royal = self.royalFlushProbability()
    straightFlush = self.straightFlushProbability()
    fourOfaKind = self.fourOfKindProbability()
    fullHouse = self.fullHouseProbability()
    flush = self.flushProbability()
    straight = self.straightProbability()
    triplets = self.threeOfKindProbability()
    twoPair = self.twoOfKindProbability()
    onePair = self.twoOfKindProbability()
    
    prob = (royal+8*straightFlush+7*fourOfaKind+6*fullHouse+5*flush+4*straight+3*triplets+2*twoPair+onePair)/9
    return prob
    
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
        return 1
      
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
        for start in range(1, 11):  
            straight = set(range(start, start+5))
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
                return 1
            elif required <= remainingDraws:
                totalCombinations = math.comb(remainingCards, remainingDraws)
                optimalCombinations = math.comb(remainingCards - required, remainingDraws - required)
                probability += optimalCombinations / totalCombinations

    return probability      
  
  def fourOfKindProbability(self):
    playerValues = [int(c[1:]) for c in self.hand]
    communityValues = [int(c[1:]) for c in self.community]
    counts = Counter(playerValues+communityValues)
    remainingDraws = 5 - len(self.community)
    remainingCards = 52 - (2*5+len(self.community))
    probability = 0
    for value in set(playerValues):
      c = counts[value]
      required = 4-c
      if required == 0:
        return 1
      if required <= remainingDraws:
        totalCombinations = math.comb(remainingCards,remainingDraws)
        optimalCombinations = math.comb(remainingCards-required, remainingDraws-required)
        probability += optimalCombinations/totalCombinations
    
    return probability
  
  def fullHouseProbability(self):
    playerValues = [int(c[1:]) for c in self.hand]
    communityValues = [int(c[1:]) for c in self.community]
    counts = Counter(playerValues + communityValues)
    remainingDraws = 5 - len(self.community)
    remainingCards = 52 - (2*5 + len(self.community))
    probability = 0

    # Case 1: both cards in hand have same value (already handled)
    if len(set(playerValues)) == 1:
        communityCounts = Counter(communityValues)
        for value in set(communityValues):
            c = communityCounts[value]
            required = 3 - c
            if required == 0:
                return 1
            if required <= remainingDraws:
                totalCombinations = math.comb(remainingCards, remainingDraws)
                optimalCombinations = math.comb(remainingCards - required, remainingDraws - required)
                probability += optimalCombinations / totalCombinations
    else:
        # Case 2: two different values in hand
        # Try to make a full house with either value as three-of-a-kind, the other as a pair
        for v1, v2 in [(playerValues[0], playerValues[1]), (playerValues[1], playerValues[0])]:
            c1 = counts[v1]
            c2 = counts[v2]
            req3 = 3 - c1
            req2 = 2 - c2
            if req3 >= 0 and req2 >= 0 and req3 + req2 <= remainingDraws:
                totalCombinations = math.comb(remainingCards, remainingDraws)
                optimalCombinations = math.comb(remainingCards - (req3 + req2), remainingDraws - (req3 + req2))
                probability += optimalCombinations / totalCombinations

        # Also check for full house using any value in community as three-of-a-kind, and either hand card as pair
        for value in set(communityValues):
            c3 = counts[value]
            for v in playerValues:
                c2 = counts[v]
                if value != v:
                    req3 = 3 - c3
                    req2 = 2 - c2
                    if req3 >= 0 and req2 >= 0 and req3 + req2 <= remainingDraws:
                        totalCombinations = math.comb(remainingCards, remainingDraws)
                        optimalCombinations = math.comb(remainingCards - (req3 + req2), remainingDraws - (req3 + req2))
                        probability += optimalCombinations / totalCombinations

    return probability
  
  
  def flushProbability(self):
    playerSuits = [c[0] for c in self.hand]
    remainingDraws = 5 - len(self.community)
    remainingCards = 52 - (2*5 + len(self.community))
    probability = 0
    
    for suit in set(playerSuits):
      playerSameSuits = [c for c in self.hand if c[0] == suit]
      communitySameSuits = [ c for c in self.community if c[0] == suit]
      required = 5- len(playerSameSuits+communitySameSuits)
      if required == 0:
        return 1
      if required <= remainingDraws:
        totalCombinations = math.comb(remainingCards,remainingDraws)
        optimalCombinations = math.comb(13-len(playerSameSuits+communitySameSuits),required) * math.comb(remainingCards-required,remainingDraws-required)
        probability +=  optimalCombinations/totalCombinations
    
    return probability
  
  
  def straightProbability(self):
    probability = 0
    remainingDraws = 5 - len(self.community)
    remainingCards = 52 - (2*5 + len(self.community))  # 2*5: 5 players, 2 cards each

    # Get all card values in hand and community
    all_values = [int(c[1:]) for c in self.hand + self.community]
    all_values = set(all_values)

    # Consider Ace as both 1 and 14 for straight
    if 1 in all_values:
        all_values.add(14)

    # Check all possible 5-card straights (A-5 to 10-14)
    possible_straights = []
    for start in range(1, 11):  # 1 to 10 (A-5 to 10-J-Q-K-A)
        straight = set(range(start, start+5))
        missing = straight - all_values
        if len(missing) <= remainingDraws:
            possible_straights.append(missing)

    # For each possible straight, calculate probability
    for missing in possible_straights:
        required = len(missing)
        if required == 0:
            # Already have straight
            return 1
        elif required <= remainingDraws:
            totalCombinations = math.comb(remainingCards, remainingDraws)
            optimalCombinations = math.comb(remainingCards - required, remainingDraws - required)
            probability += optimalCombinations / totalCombinations

    return probability
  
  def threeOfKindProbability(self):
    probability = 0
    remainingDraws = 5 - len(self.community)
    remainingCards = 52 - (2*5 + len(self.community)) 
    
    playerValues = [int(c[1:]) for c in self.hand]
    communityValues = [int(c[1:]) for c in self.community]
    counts = Counter(playerValues+communityValues)
    for value in playerValues:
      c = counts[value]
      required = 3-c
      if required <= 0:
        return 1
      if required <= remainingDraws:
        totalCombinations = math.comb(remainingCards, remainingDraws)
        optimalCombinations = math.comb(4-c,required) * math.comb(remainingCards - required, remainingDraws - required)
        probability += optimalCombinations / totalCombinations
    
    return probability
      
  def twoOfKindProbability(self):
    probability = 0
    remainingDraws = 5 - len(self.community)
    remainingCards = 52 - (2*5 + len(self.community)) 
    
    playerValues = [int(c[1:]) for c in self.hand]
    communityValues = [int(c[1:]) for c in self.community]
    counts = Counter(playerValues+communityValues)
    for value in playerValues:
      c = counts[value]
      required = 2-c
      if required <= 0:
        return 1
      if required <= remainingDraws:
        totalCombinations = math.comb(remainingCards, remainingDraws)
        optimalCombinations = math.comb(3-c,required) * math.comb(remainingCards - required, remainingDraws - required)
        probability += optimalCombinations / totalCombinations
    
    return probability
    

  


  



    
    