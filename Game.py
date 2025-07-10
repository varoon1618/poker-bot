import Player
import random

class Game:
  players = []
  spades = ["s1","s2","s3","s4","s5","s6","s7","s8","s9","s10","s11","s12","s13"]
  hearts = ["h1","h2","h3","h4","h5","h6","h7","h8","h9","h10","h11","h12","h13"]
  clubs = ["c1","c2","c3","c4","c5","c6","c7","c8","c9","c10","c11","c12","c13"]
  diamonds = ["d1","d2","d3","d4","d5","d6","d7","d8","d9","d10","d11","d12","d13"]
  cards = spades + hearts + clubs + diamonds
  state = -1
  stateDict = {0:'buy in',1:'deal cards',2:'bet',3:'flop',4:'bet',
               5: 'turn', 6: 'bet', 7:'river',8:'bet',9:'showdown',10:'winner' }
  
  pot = 0
  
    
  def main(self):
    self.initialiseGame()
    while(self.state<1):
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
      self.dealCards()
      for player in self.players:
        print("Player "+player.name+"'s hand is: "+ player.printHand())
  
  def initialiseRound(self):
    self.cards = self.spades + self.hearts + self.clubs + self.diamonds
    for player in self.players:
      player.resetPlayer()
    
  
  def addPlayer(self,player):
    self.players.append(player)
    
  def collectBuyIns(self,buyIn):
    for player in self.players:
      if(buyIn < player.money):
        self.pot = self.pot + player.bet(buyIn)
      else:
        print("Player "+player.name+" cannot afford buy in, kicked out")
        self.players.remove(player)
  
  def dealCards(self):
    for player in self.players:
      index1 = random.randint(0,len(self.cards)-1)
      card1 = self.cards[index1]
      self.cards.remove(card1)
      index2 = random.randint(0,len(self.cards)-1)
      card2 = self.cards[index2]
      player.setHand(card1)
      player.setHand(card2)
  
    
  
    
  