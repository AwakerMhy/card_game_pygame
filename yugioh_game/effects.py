"""
卡牌效果实现
"""
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .game_state import GameState


def effect_pot_of_greed(state: "GameState", player_id: str) -> "GameState":
    """强欲之壶：抽2张卡"""
    player = state.get_player(player_id)
    player.draw(2)
    return state


def effect_monster_reborn(state: "GameState", player_id: str, grave_index: int = 0) -> "GameState":
    """死者苏生：从双方墓地特殊召唤1只怪兽，优先己方"""
    player = state.get_player(player_id)
    p1_mon = state.player1.get_graveyard_monsters()
    p2_mon = state.player2.get_graveyard_monsters()
    if player_id == "player1":
        monsters = p1_mon + p2_mon
    else:
        monsters = p2_mon + p1_mon
    if grave_index < 0 or grave_index >= len(monsters):
        return state
    card = monsters[grave_index]
    zone_idx = player.field.get_empty_monster_index()
    if zone_idx is None:
        return state
    if card in state.player1.graveyard:
        state.player1.graveyard.remove(card)
    else:
        state.player2.graveyard.remove(card)
    from .field import create_monster_slot
    player.field.monster_zones[zone_idx] = create_monster_slot(card, "attack", summoned_this_turn=True)
    return state


def effect_dark_hole(state: "GameState") -> "GameState":
    """黑洞：破坏场上所有怪兽"""
    for p in [state.player1, state.player2]:
        for i, slot in enumerate(p.field.monster_zones):
            if slot:
                p.send_to_graveyard(slot["card"])
                p.field.monster_zones[i] = None
    return state


def effect_mirror_force(state: "GameState", attacker_player_id: str) -> "GameState":
    """圣防护罩：破坏对手所有攻击表示怪兽"""
    defender = state.get_opponent() if state.current_player == attacker_player_id else state.get_current_player()
    defender = state.player2 if attacker_player_id == "player1" else state.player1
    for i, slot in enumerate(defender.field.monster_zones):
        if slot and slot["position"] == "attack":
            defender.send_to_graveyard(slot["card"])
            defender.field.monster_zones[i] = None
    return state
