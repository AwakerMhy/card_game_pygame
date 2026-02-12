"""
游戏状态管理：GameState、TurnPhase 状态机
"""
from dataclasses import dataclass, field
from typing import Optional, Tuple
from .card import Card
from .player import Player
from .card_database import create_starter_deck


@dataclass
class GameState:
    """全局游戏状态"""
    player1: Player
    player2: Player
    current_player: str      # "player1" | "player2"
    current_phase: str      # draw/standby/main1/battle/main2/end
    turn_count: int = 0
    is_first_turn: bool = True
    game_over: bool = False
    winner: Optional[str] = None
    normal_summoned_this_turn: bool = False

    def get_current_player(self) -> Player:
        return self.player1 if self.current_player == "player1" else self.player2

    def get_opponent(self) -> Player:
        return self.player2 if self.current_player == "player1" else self.player1

    def get_player(self, player_id: str) -> Player:
        return self.player1 if player_id == "player1" else self.player2


def init_game_state() -> GameState:
    """初始化游戏"""
    deck1 = create_starter_deck()
    deck2 = create_starter_deck()
    p1 = Player("player1", deck1)
    p2 = Player("player2", deck2)
    p1.shuffle_deck()
    p2.shuffle_deck()
    p1.draw(5)
    p2.draw(5)
    return GameState(
        player1=p1,
        player2=p2,
        current_player="player1",
        current_phase="draw",
        turn_count=1,
        is_first_turn=True,
    )


def set_phase_for_testing(state: GameState, phase: str = "main1"):
    """测试用：设置阶段"""
    state.current_phase = phase
