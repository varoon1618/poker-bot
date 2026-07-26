from Strategies import CombinatorialStrategy

class BotController:
  def __init__(self,strategy=None):
    if strategy is None:
      self.strategy = CombinatorialStrategy()
    else:
      self.strategy = strategy
  
  def set_strategy(self,strategy):
    self.strategy = strategy
  
  def make_decision(self,state):
    action,amount = self.strategy.decide(state=state)
    return action,amount
