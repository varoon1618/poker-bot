class HandRank:
  def __init__(self, rank_name:str,rank_type:int, rank_value:int, kickers:list[int]):
    self.rank_name = rank_name
    self.rank_type = rank_type 
    self.rank_value = rank_value 
    self.kickers = kickers  
  
  def __lt__(self, other):
    if self.rank_type != other.rank_type:
      return self.rank_type < other.rank_type
    
    if self.rank_value != other.rank_value:
      return self.rank_value < other.rank_value
    
    return self.kickers < other.kickers

  def __eq__(self, other):
    return (self.rank_type == other.rank_type and 
            self.rank_value == other.rank_value and 
            self.kickers == other.kickers)
