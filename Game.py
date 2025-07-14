import Player
import random

'''
TO DO:

Add big blind, small blind -make sure it rotates each round

Calculate different ways of winning/who won

Keepingtrack of who folded, who is playing , who is totally out of table(doesnt have enough money)

Add frontend 

Any bugs ?

'''

class Game:
  players = []
  communityCards = []
  spades = ["s1","s2","s3","s4","s5","s6","s7","s8","s9","s10","s11","s12","s13"]
  hearts = ["h1","h2","h3","h4","h5","h6","h7","h8","h9","h10","h11","h12","h13"]
  clubs = ["c1","c2","c3","c4","c5","c6","c7","c8","c9","c10","c11","c12","c13"]
  diamonds = ["d1","d2","d3","d4","d5","d6","d7","d8","d9","d10","d11","d12","d13"]
  cards = spades + hearts + clubs + diamonds
  state = -1
  stateDict = {0:'buy in',1:'deal cards',2:'bet',3:'flop',4:'bet',
               5: 'turn', 6: 'bet', 7:'river',8:'bet',9:'showdown',10:'winner' }
  previousBet = 5
  pot = 0
  
  
  def main(self):
    self.initialiseGame()
    while(self.state<11):
      self.playGame()
  
  
  def initialiseGame(self):
    player1 = Player.Player()
    player2 = Player.Player()
    player1.init(1,"varun",500)
    player2.init(2,"bot",500)
    self.addPlayer(player1)
    self.addPlayer(player2)
    self.state = 0
    
  
  def playGame(self):
    if(self.state == 0):
      self.initialiseRound()
      print("collecting buy ins")
      self.collectBuyIns(5)
      self.state = 1
      
    if(self.state == 1):
      self.previousBet = 5
      self.dealCards()
      for player in self.players:
        print("Player "+player.name+"'s hand is: "+ player.printHand())
      self.state = 2
    
    if(self.state in [2,4,6,8]):
      self.previousBet = 5
      self.collectBets()
      #print("total pot: ",self.pot)
      if(not(self.checkGameOver())):
        self.state +=1
      else:
        self.state=10
    
    if(self.state==3):
      self.previousBet = 5
      self.dealFlop()
      print("flop: "+ ' '.join(str(card) for card in self.communityCards))
      self.state=4
      
    if (self.state==5 or self.state==7):
      self.previousBet = 5
      self.dealRandomCard()
      print('community cards: ', " ".join(str(card) for card in self.communityCards))
      self.state += 1
      
    if (self.state == 9):
      for player in [p for p in self.players if not(p.fold)]:
        print(player.name,'has hand: ',player.printHand())
      
      print('community cards: ', " ".join(str(card) for card in self.communityCards))
      self.state +=1
    
    if (self.state==10):
      print("The winner is: ", self.calculateWinner())
      self.state = 11
    
  def initialiseRound(self):
    self.cards = self.spades + self.hearts + self.clubs + self.diamonds
    self.pot = 0
    for player in self.players:
      player.resetPlayer()
    
  
  def addPlayer(self,player):
    self.players.append(player)
    
  def collectBuyIns(self,buyIn):
    for player in self.players:
      if(buyIn < player.money) and not(player.fold):
        self.pot = self.pot + player.bet(buyIn)
      else:
        print("Player "+player.name+" cannot afford buy in, kicked out")
        self.players.remove(player)
  
  def dealCards(self):
    for player in self.players:
      indexes = random.sample(range(0,len(self.cards)),2)
      index1,index2 = indexes[0],indexes[1]
      card1,card2 = self.cards[index1],self.cards[index2]
      player.setHand(card1)
      player.setHand(card2)
      self.cards.remove(card1)
      self.cards.remove(card2)
  
  
  def collectBets(self):
    for player in [p for p in self.players if not(p.fold)]:
      if(player.name == "varun"):
        print("What is your next move ?")
        print("Previous bet: ",self.previousBet)
        print("Type 1 to fold, 2 to match previous bet, 3 to raise")
        n = int(input("Enter Value: "))
        if(n==1):
          player.fold = True
        if(n==2):
          player.bet(self.previousBet)
          self.pot = self.pot + self.previousBet
        else:
          bet = int(input("Enter how much do you want to bet: "))
          player.bet(bet)
          self.previousBet = bet
          self.pot = self.pot + bet
      else:
        player.bet(self.previousBet)
        self.pot = self.pot + self.previousBet
  
  def dealFlop(self):
    indexes = random.sample(range(0,len(self.cards)),3)
    index1,index2,index3= indexes[0],indexes[1],indexes[2]
    card1,card2,card3 = self.cards[index1],self.cards[index2], self.cards[index3]
    self.communityCards.extend([card1,card2,card3])
    self.cards.remove(card1)
    self.cards.remove(card2)
    self.cards.remove(card3)
    for player in self.players:
      player.setCommunityCards(self.communityCards)
  
  def dealRandomCard(self):
    index = random.randint(0,len(self.cards)-1)
    card = self.cards[index]
    self.communityCards.append(card)
    self.cards.remove(card)
    for player in self.players:
      player.setCommunityCards(self.communityCards)
  
  def checkGameOver(self):
    if(len([p for p in self.players if not(p.fold)]) == 1):
      return True
    return False
  
  def calculateWinner(self):
    remainingPlayers = [p for p in self.players if not(p.fold)]
    if(len(remainingPlayers) ==1):
      return remainingPlayers[0].name
    else:
      scores = [self.scoreHand(p) for p in remainingPlayers]
      highest = max(scores)
      if(scores.count(highest) ==1):
        return remainingPlayers[scores.index(highest)].name
      else:
        print("Tie Breaker")
        tiebreaker = [remainingPlayers[i] for i, score in enumerate(scores) if score == highest]
        # Find the player with the highest card value
        def get_highest_card(player):
            all_cards = player.hand + self.communityCards
            values = [int(c[1:]) for c in all_cards]
            return max(values)
        winner = max(tiebreaker, key=get_highest_card)
        return winner.name
  
  def scoreHand(self,player):
    if self.isSameSuit(player):
      if self.isConsecutive(player):
        if self.isRoyalFlush(player):
          return 10 #royal flush
        else:
          return 9 #straight flush
      else:
        return 6 #flush
    
    if self.isSameValue(player):
      return 8 #four of a kind
    
    if self.isConsecutive(player):
      return 5 #straight
    
    if (self.returnTriplets(player)>0):
      if(self.returnPairs(player)==1):
        return 7 #full house
      else:
        return 4 #three of a kind
    
    if(self.returnPairs(player)==2):
      return 3 # 2 pairs
    
    if(self.returnPairs(player)==1):
      return 2 # 1 pair
    
    return 1 #nothing 
  
  
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
    
  '''
  Royal FLush - A,K,Q,J,10 - all same suite
  
  Straight Flush - same suit with 5 consecutive vlaues from that suit
  
  Four of a kind 
  
  Full house - 3 of a kind + 2 of a kind
  
  Flush - 5 cards same suit, can be in any order 
  
  Straight - 5 consecutive cards of any suit
  
  Three of a kind 
  
  Two pairs
  
  One Pair
  
  High card - if none of the above then the person with highest card wins, if both
  players have same highest card, second highest card is used 
  '''
  
    
    
  
    
  