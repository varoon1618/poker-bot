from dataclasses import dataclass, field
from typing import List, Optional, Any
from GameElements import Player,Card

@dataclass
class GameState:
  pot: int = 0
  current_player: Optional[Player] = None
  round: Optional[str] = None
  community_cards: List[Card] = field(default_factory=list)
  prev_bet: int = 0
  players: List[Player] = field(default_factory=list)
  num_raises: int = 0
  exception: Optional[Exception] = None
  new_round: bool = False
  winners: Optional[List['Player']] = None
  game_complete: bool = False
  winning_rank_name: Optional[str] = None
  max_raises_round: int = 2
  can_continue_betting: bool = False
  can_continue_game: bool = False

  @classmethod
  def from_game_engine(cls, engine):
    attrs = {
      'pot': engine.pot,
      'current_player': engine.players[engine.current_player_idx],
      'round': engine.round,
      'community_cards': engine.community_cards,
      'prev_bet': engine.prev_bet,
      'players': engine.players,
      'num_raises': engine.num_raises,
      'exception': engine.exception,
      'new_round': engine.new_round,
      'winners': engine.winners,
      'game_complete': engine.game_complete,
      'winning_rank_name': engine.winning_rank_name,
      'max_raises_round': engine.MAX_RAISES_ROUND,
      'can_continue_betting': engine.can_continue_betting,
      'can_continue_game': engine.can_continue_game,
    }
    return cls(**attrs)