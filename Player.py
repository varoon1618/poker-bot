class Player:
  playerID = -1
  name = "default"
  money = -1
  fold = False
  hasActed = False
  hand = []
  type = ""
  communityCards = []
  
  def init(self,playerID,name,money,type):
    self.playerID = playerID
    self.name = name
    self.money = money
    self.type = type
  
  def bet(self,bet):
    if(bet<self.money):
      self.money = self.money - bet
    else:
      print("bet is larger that the current amount")
    return bet
  
  def get_money(self):
    return self.money
  
  def add_winnings(winnings,self):
    self.money = self.money + winnings
    
  def call(previousBet,self):
    if previousBet > self.money:
      self.bet(self.money)
    else:
      self.money = self.money - previousBet
      self.bet(previousBet)
  
  def raiseBet(previousBet,newBet,self):
    if newBet<previousBet:
      print("Error while raising(amount has to larger than previous bet)")
    else:
      self.bet(newBet)
  
  def foldTurn(self):
    self.fold = True
    return "fold"
  
  def setFold(self,value):
    self.fold = value
  
  def setHand(self,card):
    self.hand.append(card)
  
  def setCommunityCards(self,community):
    self.communityCards = community
  
  def resetPlayer(self):
    self.hand = []
    self.fold = False
    self.communityCards = []
    
  def printHand(self):
    return ' '.join(str(card) for card in self.hand)
    
  
  
  