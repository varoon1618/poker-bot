import Player
import random
import datetime
import Estimator
from collections import Counter
'''
TO DO:

Add big blind, small blind -make sure it rotates each round

Add frontend 

Any bugs ?

Add split pot logic in case of ties even after tie breaker
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
  estimator  = None
  lastRaised = None
  
  def __init__(self,gui,action_queue):
    self.callBackId = None
    self.gui = gui
    self.action_queue = action_queue
    player1 = Player.Player()
    player2 = Player.Player()
    player3 = Player.Player()
    player4 = Player.Player()
    player5 = Player.Player()
    
    self.estimator = Estimator.Estimator()
    player2.init(1,"bot1",500,"bot")
    player3.init(2,"bot2",500,"bot")
    player1.init(3,"varun",500,"human")
    player4.init(4,"bot3",500,"bot")
    player5.init(5,"bot4",500,"bot")
    
    self.addPlayer(player2)
    self.addPlayer(player3)
    self.addPlayer(player1)
    self.addPlayer(player4)
    self.addPlayer(player5)
    self.state = 0
  
  
  def playGame(self):
    
    activeBots = [p for p in self.players if p.type=="bot" and not(p.fold)]
    self.gui.reset_bot_action_labels(activeBots)
    
    
    if(self.state == 0):
      self.initialiseRound()
      self.gui.update_status("Collecting Buy Ins")
      print("collecting buy ins")
      self.collectBuyIns(5)
      
    if(self.state == 1):
      self.previousBet = 5
      self.gui.update_previousBet(self.previousBet)
      self.dealCards()
      for player in self.players:
        print("Player "+player.name+"'s hand is: "+ player.printHand())
    
    if(self.state in [2,4,6,8]):
      self.previousBet = 5
      self.gui.update_previousBet(self.previousBet)
      self.gui.update_status("Place your bets")
      self.collectBets(done_callback=self.afterBets)
      
    if(self.state==3):
      self.previousBet = 5
      self.gui.update_previousBet(self.previousBet)
      self.dealFlop()
      print("flop: "+ ' '.join(str(card) for card in self.communityCards))
      self.gui.update_community(self.communityCards)
      
    if (self.state==5 or self.state==7):
      self.previousBet = 5
      self.gui.update_previousBet(self.previousBet)
      self.dealRandomCard()
      print('community cards: ', " ".join(str(card) for card in self.communityCards))
      self.gui.update_community(self.communityCards)

      
    if (self.state == 9):
      for player in [p for p in self.players if not(p.fold)]:
        print(player.name,'has hand: ',player.printHand())
      print('community cards: ', " ".join(str(card) for card in self.communityCards))
      self.state +=1
      self.playGame()
    
    if (self.state==10):
      winner  = self.calculateWinner()
      print("The winner is: ", winner)
      self.gui.update_status("The winner is: " +str(winner) )
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
    self.gui.update_pot(self.pot)
    self.state = 1
    self.playGame()
  
  def dealCards(self):
    for player in self.players:
      indexes = random.sample(range(0,len(self.cards)),2)
      index1,index2 = indexes[0],indexes[1]
      card1,card2 = self.cards[index1],self.cards[index2]
      player.setHand(card1)
      player.setHand(card2)
      self.cards.remove(card1)
      self.cards.remove(card2)
      if player.type == "human":
        self.gui.update_hand(player.hand)
      self.gui.updateMoney(player)
      self.gui.update_current_player(player.playerID)
    self.state = 2
    self.playGame()
  
  def collectBets(self, done_callback = None):
    self.activePlayers = [p for p in self.players if not p.fold]
    self.betIndex = 0
    self._process_next_bet(done_callback)

  def _process_next_bet(self, done_callback):
    
    #print(f"function called at {datetime.datetime.now().strftime('%H:%M:%S')}")
    
    if self.callBackId:  # Cancel any pending after()
      #print("cancelling callback")
      self.gui.master.after_cancel(self.callBackId)
      self.callBackId = None

    if self.betIndex >= len(self.activePlayers):
      if all([p.hasActed for p in self.activePlayers]):  
        if done_callback:
            self.gui.master.after(3000,lambda: done_callback())
        return
      else:
        self.betIndex = 0
        self.callBackId = self.gui.master.after(3000, lambda: self.collectBets(done_callback=self.afterBets))
        print('bello')
        print([p.hasActed for p in self.activePlayers])
        
    player = self.activePlayers[self.betIndex]
    
    if player == self.lastRaised or player.hasActed == True:
      print(f'Player {player.name} already raised this round')
      self.betIndex += 1
      self.callBackId = self.gui.master.after(100, lambda: self._process_next_bet(done_callback))
      return 
    
    if player.type == "human":
      self.gui.update_playerTurn(True)
      self.gui.update_current_player(player.playerID)
      if not self.action_queue.empty():
        action = self.action_queue.get()
        if action["action"] == "fold":
          player.fold = True
          player.hasActed = True
        elif action["action"] == "call":
          player.hasActed = True
          player.bet(self.previousBet)
          self.pot += self.previousBet
          self.gui.update_pot(self.pot)
          self.gui.update_move("you called")
        elif action["action"] == "raise":
          self.lastRaised = player
          bet = int(action["amount"])
          player.hasActed = True
          for p in self.activePlayers:
            if p != player:
              p.hasActed = False
          player.bet(bet)
          self.pot += bet
          self.gui.update_pot(self.pot)
          self.previousBet = bet
          self.gui.update_previousBet(self.previousBet)
          self.gui.update_move("You raised to "+ str(bet))
        
        self.gui.updateMoney(player)
        self.gui.update_playerTurn(False)
        self.betIndex += 1
        self.callBackId = self.gui.master.after(500, lambda: self._process_next_bet(done_callback))
      else:
        self.gui.update_move("Waiting for your move...")
        self.callBackId = self.gui.master.after(100, lambda: self._process_next_bet(done_callback))
    else:
      #self.callBackId = self.gui.master.after(3000, lambda: self.processBotAction(player, done_callback))
      self.processBotAction(player, done_callback)
      self.gui.updateMoney(player)
      self.gui.update_current_player(player.playerID)

  def processBotAction(self, player, done_callback):
      print(f"{player.name} acting at {datetime.datetime.now().strftime('%H:%M:%S')}")
      bestMove = self.estimator.returnBestMove(player,self.pot,self.previousBet)
      print(f'Bot: {player.name}, Best Move {bestMove}')
      if(bestMove['action'] == "raise"):
        self.lastRaised = player
        bet = bestMove['bet']
        player.hasActed = True
        for p in self.activePlayers:
          if p != player and p.playerID < player.playerID and not(p.fold):
            p.hasActed = False
          
        self.gui.update_move(f'Bot: {player.name} raised to {bet}')
        player.bet(bet)
        self.pot += bet
        self.gui.update_pot(self.pot)
        self.previousBet = bet
        self.gui.update_previousBet(self.previousBet)
        self.gui.update_bot_action(player,{'action':'raise','amount':bet})
        self.betIndex +=1
        self.callBackId = self.gui.master.after(3000, lambda: self._process_next_bet(done_callback))
      
      if(bestMove['action'] == 'call'):
        self.gui.update_move(f"Bot: {player.name} called")
        player.bet(self.previousBet)
        player.hasActed = True
        self.pot += self.previousBet
        self.gui.update_pot(self.pot)
        self.gui.update_bot_action(player,{'action':'call','amount':self.previousBet})
        self.betIndex += 1
        self.callBackId = self.gui.master.after(3000, lambda: self._process_next_bet(done_callback))
      
      if(bestMove['action'] == 'fold'):
        self.gui.update_move(f'Bot: {player.name} folded')
        player.fold = True
        player.hasActed = True
        self.gui.update_bot_action(player,{'action':'fold','amount':0})
        self.betIndex += 1
        self.callBackId = self.gui.master.after(3000, lambda: self._process_next_bet(done_callback))
        
  
  
  def afterBets(self):
    print("total pot: ",self.pot)
    if(not(self.checkGameOver())):
      for player in self.activePlayers:
        player.hasActed = False
      print(f'resetting active players {[p.name for p in self.activePlayers]}')
      self.state +=1
    else:
      self.state=10
    print("game state:", self.state)
    self.playGame()

    
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
    self.state=4
    self.playGame()
  
  def dealRandomCard(self):
    index = random.randint(0,len(self.cards)-1)
    card = self.cards[index]
    self.communityCards.append(card)
    self.cards.remove(card)
    for player in self.players:
      player.setCommunityCards(self.communityCards)
    self.state += 1
    self.playGame()
  
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
        winner = self.break_tie(tiebreaker)
        if isinstance(winner,list):
          print("Tie between: ", [p.name for p in winner])
          return winner[0].name
        else:
          return winner.name
  
  def break_tie(self,players):

    def get_sorted_hand(player):
        # Combine hand and community, convert to int, sort descending
        all_cards = player.hand
        values = [int(c[1:]) for c in all_cards]
        # Ace can be high (14) or low (1), but for high card, treat as 14
        if 1 in values:
            values.append(14)
            values.remove(1)
        return sorted(values, reverse=True)

    tied_players = players
    hand_lists = {p: get_sorted_hand(p) for p in tied_players}

    for i in range(2):
        # Find the highest value at this position among all tied players
        current_max = max((hand[i] for hand in hand_lists.values() if len(hand) > i), default=None)
        # Filter players who have this value at this position
        tied_players = [p for p in tied_players if len(hand_lists[p]) > i and hand_lists[p][i] == current_max]
        if len(tied_players) == 1:
            return tied_players[0]  # Winner found

    # If still tied after all cards, return all tied players (split pot)
    return tied_players
  
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
    sameSuitCounts = []
    playerSuits = [c[0] for c in player.hand]
    for suit in playerSuits:
      playerSameSuits = [c for c in player.hand if c[0]==suit]
      communitySameSuits = [c for c in self.communityCards if c[0]==suit]
      sameSuitCounts.append(len(playerSameSuits + communitySameSuits))
    return max(sameSuitCounts) >= 5


  def isConsecutive(self, player):
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

    return max_count >= 5

  
  def isSameValue(self,player):
    cards = player.hand+ self.communityCards
    values = [int(c[1:]) for c in cards]
    uniq = sorted(set(values))
    count=max_count=1
    
    for i in range(1,len(uniq)):
      if uniq[i] == uniq[i-1]:
        count += 1
        max_count = max(max_count,count)
      else:
        count = 1
    
    return max_count >= 4
  
  def returnPairs(self,player):
    cards = player.hand+self.communityCards
    values = [int(c[1:]) for c in cards]
    print(values)
    counts = Counter(values)
    pairs = 0
    for c in counts.values():
      if c==2:
        pairs +=1 
    print(f"pairs {pairs}")
    return pairs
  
  def returnTriplets(self,player):
    cards = player.hand+self.communityCards
    values = [int(c[1:]) for c in cards]
    counts = Counter(values)
    triplets = 0
    for c in counts.values():
      if c==3:
        triplets +=1 
    return triplets
  
  def isRoyalFlush(self,player):
    flushValues ={1,10,11,12,13}
    cards = player.hand + self.communityCards
    playerSuits = [c[0] for c in player.hand]
    flushCount = maxCount = 0
    for suit in set(playerSuits):
      flushCards = [c for c in cards if c[0] ==suit and int(c[1:]) in flushValues]
      flushCount = len(flushCards)
      maxCount = max(flushCount,maxCount)
    
    return maxCount >=5

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
  
    
    
  
    
  