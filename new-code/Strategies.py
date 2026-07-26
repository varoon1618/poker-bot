from abc import ABC, abstractmethod
from GameElements import GameState

class BotStrategy(ABC):
  @abstractmethod
  def decide(self,state:GameState):
    '''Takes in Gamestate, and returns 
    Action (CALL,FOLD,RAISE), with optional AMOUNT'''
    pass

class CombinatorialStrategy(BotStrategy):
  def decide(self,state):
    return "RAISE",10