"""
阶段切换逻辑：抽卡、阶段推进、回合结束
"""
from .game_state import GameState

PHASE_ORDER = ["draw", "standby", "main1", "battle", "main2", "end"]


def advance_phase(state: GameState, run_ai: bool = True) -> bool:
    """
    推进到下一阶段
    返回 True 表示阶段已切换
    """
    if state.current_phase == "end":
        on_enter_end(state)
        return True
    idx = PHASE_ORDER.index(state.current_phase) if state.current_phase in PHASE_ORDER else 0
    next_idx = idx + 1
    new_phase = PHASE_ORDER[next_idx]
    if new_phase == "battle" and should_auto_skip_battle(state):
        new_phase = "main2"
    state.current_phase = new_phase
    if new_phase == "draw":
        on_enter_draw(state)
    if run_ai and state.current_player == "player2":
        from .ai import ai_turn
        ai_turn(state)
    return True


def on_enter_draw(state: GameState):
    """进入抽卡阶段"""
    current = state.get_current_player()
    if state.is_first_turn and state.current_player == "player1":
        pass
    else:
        current.draw(1)


def on_enter_end(state: GameState):
    """结束阶段：切换控制权、重置回合标记、进入新回合抽卡阶段"""
    state.current_player = "player2" if state.current_player == "player1" else "player1"
    state.turn_count += 1
    state.is_first_turn = False
    state.normal_summoned_this_turn = False
    current = state.get_current_player()
    for slot in current.field.monster_zones:
        if slot:
            slot["attacked_this_turn"] = False
            slot["changed_position_this_turn"] = False
            slot["summoned_this_turn"] = False
    state.current_phase = "draw"
    on_enter_draw(state)


def can_skip_battle(state: GameState) -> bool:
    """是否可以跳过战斗阶段"""
    current = state.get_current_player()
    has_attack = any(
        s and s["position"] == "attack" and not s["attacked_this_turn"]
        for s in current.field.monster_zones
    )
    return not has_attack


def should_auto_skip_battle(state: GameState) -> bool:
    """先攻首回合无战斗阶段"""
    return state.is_first_turn and state.current_player == "player1"
