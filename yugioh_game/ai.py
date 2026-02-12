"""
AI 对手：简单决策树
"""
import random
from .game_state import GameState
from .card import Position


def ai_turn(state: GameState) -> bool:
    """
    AI 执行一个完整回合
    当 AI 需要操作时返回 True，否则 False
    """
    if state.current_player != "player2":
        return False
    current = state.get_current_player()
    # 主阶段1：召唤、盖放
    if state.current_phase == "main1":
        _ai_main_phase(state)
        return True
    if state.current_phase == "battle":
        _ai_battle_phase(state)
        return True
    return False


def _ai_main_phase(state: GameState):
    """主阶段：召唤攻击力最高的怪兽，盖放陷阱"""
    current = state.get_current_player()
    if not state.normal_summoned_this_turn:
        summonable = [c for c in current.hand if c.is_monster() and c.level <= 4]
        if not summonable:
            summonable = [c for c in current.hand if c.is_monster()]
        if summonable:
            card = max(summonable, key=lambda c: c.atk)
            idx = current.hand.index(card)
            needed = current.get_tribute_count(card.level)
            zone_idx = current.field.get_empty_monster_index()
            if zone_idx is not None:
                if needed == 0:
                    current.summon_monster(idx, zone_idx, "attack", [])
                    state.normal_summoned_this_turn = True
                elif needed <= sum(1 for s in current.field.monster_zones if s):
                    tributes = [i for i, s in enumerate(current.field.monster_zones) if s]
                    if len(tributes) >= needed:
                        tributes = tributes[:needed]
                        current.summon_monster(idx, zone_idx, "attack", tributes)
                        state.normal_summoned_this_turn = True
    if random.random() < 0.5:
        spells = [c for c in current.hand if c.is_spell() and c.subtype == "normal"]
        if spells and state.current_phase in ("main1", "main2"):
            from .effects import effect_pot_of_greed, effect_dark_hole, effect_monster_reborn
            card = random.choice(spells)
            base_id = card.card_id.split("_")[0] if "_" in card.card_id else card.card_id
            idx = current.hand.index(card)
            current.hand.pop(idx)
            current.send_to_graveyard(card)
            if base_id == "s001":
                effect_pot_of_greed(state, "player2")
            elif base_id == "s002":
                if current.get_graveyard_monsters() or state.player1.get_graveyard_monsters():
                    effect_monster_reborn(state, "player2", 0)
            elif base_id == "s003":
                effect_dark_hole(state)
    if random.random() < 0.7:
        traps = [c for c in current.hand if c.is_trap()]
        if traps:
            card = random.choice(traps)
            idx = current.hand.index(card)
            zone_idx = current.field.get_empty_spell_trap_index()
            if zone_idx is not None:
                current.set_spell_trap(idx, zone_idx, False, state.turn_count)


def _ai_battle_phase(state: GameState):
    """战斗阶段：攻击"""
    from .battle import calc_battle, apply_battle_result
    current = state.get_current_player()
    opponent = state.player1
    attackers = current.field.get_attack_position_monsters()
    for zone_idx, slot in attackers:
        if slot["attacked_this_turn"]:
            continue
        if not any(opponent.field.monster_zones):
            res = calc_battle(slot["card"], slot["position"], None)
            apply_battle_result(current, opponent, zone_idx, None, res)
            break
        targets = [(i, s) for i, s in enumerate(opponent.field.monster_zones) if s]
        if targets:
            def key(t):
                i, s = t
                c = s["card"]
                if s["position"] == Position.ATTACK:
                    return c.atk
                return c.def_
            target_idx, target_slot = min(targets, key=key)
            res = calc_battle(slot["card"], slot["position"], target_slot)
            if res.get("flip_defender"):
                opponent.field.monster_zones[target_idx]["position"] = Position.DEFENSE
            apply_battle_result(current, opponent, zone_idx, target_idx, res)
            break
