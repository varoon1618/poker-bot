class GameState:
  def __init__(self,**kwargs):
    self.pot = kwargs.get('pot',0)
    self.current_player = kwargs.get('current_player')
    self.round = kwargs.get('round')
    self.community_cards = kwargs.get('community_cards',[])
    self.prev_bet = kwargs.get('prev_bet',0)
    self.players = kwargs.get('players',[])
    self.num_raises = kwargs.get('num_raises',0)
    self.exception = kwargs.get('exception',None)
    self.new_round = kwargs.get('new_round',False)
    self.winners = kwargs.get('winners',None)
    self.game_complete = kwargs.get('game_complete',False)
    self.winning_rank_name = kwargs.get('winning_rank_name',None)
    self.max_raises_round = kwargs.get('max_raises_round',2)
    self.can_continue_betting = kwargs.get('can_continue_betting',False)
    self.can_continue_game = kwargs.get('can_continue_game',False)

  
  @classmethod
  def from_game_engine(cls,engine):
    current_player = engine.players[engine.current_player_idx]
    players = engine.players
    pot = engine.pot
    community_cards = engine.community_cards
    round = engine.round
    prev_bet = engine.prev_bet
    num_raises = engine.num_raises
    exception = engine.exception
    new_round = engine.new_round
    winners = engine.winners
    game_complete = engine.game_complete
    winning_rank_name = engine.winning_rank_name
    max_raises_round = engine.MAX_RAISES_ROUND
    can_continue_betting = engine.can_continue_betting
    can_continue_game = engine.can_continue_game
    
    return cls(current_player=current_player,pot=pot,community_cards=community_cards,
               round = round, prev_bet=prev_bet,players = players, num_raises=num_raises,
               exception = exception,new_round=new_round,winners=winners,
               game_complete=game_complete, winning_rank_name=winning_rank_name,
               max_raises_round=max_raises_round,can_continue_betting=can_continue_betting,
               can_continue_game =can_continue_game)

