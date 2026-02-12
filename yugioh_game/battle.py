"""
战斗计算逻辑：纯函数，无副作用
"""
from typing import Optional, Tuple
from .card import Card, Position


def calc_battle(attacker: Card, attacker_pos: str,
                defender_slot: Optional[dict] = None) -> dict:
    """
    战斗伤害计算
    attacker: 攻击方怪兽
    attacker_pos: 攻击方表示形式 (应为 attack)
    defender_slot: 防御方怪兽区卡位，None 表示直接攻击

    返回:
    {
        "attacker_destroyed": bool,
        "defender_destroyed": bool,
        "attacker_damage": int,   # 攻击方玩家受到的伤害
        "defender_damage": int,   # 防御方玩家受到的伤害
        "flip_defender": bool,    # 是否翻开里侧怪兽
    }
    """
    result = {
        "attacker_destroyed": False,
        "defender_destroyed": False,
        "attacker_damage": 0,
        "defender_damage": 0,
        "flip_defender": False,
    }
    if attacker_pos != Position.ATTACK:
        return result
    if defender_slot is None:
        result["defender_damage"] = attacker.atk
        return result
    defender = defender_slot["card"]
    def_pos = defender_slot["position"]
    if def_pos == Position.SET:
        result["flip_defender"] = True
        def_pos = Position.DEFENSE
    if def_pos == Position.ATTACK:
        if attacker.atk > defender.atk:
            result["defender_destroyed"] = True
            result["defender_damage"] = attacker.atk - defender.atk
        elif attacker.atk < defender.atk:
            result["attacker_destroyed"] = True
            result["attacker_damage"] = defender.atk - attacker.atk
        else:
            result["attacker_destroyed"] = True
            result["defender_destroyed"] = True
    else:
        if attacker.atk > defender.def_:
            result["defender_destroyed"] = True
        elif attacker.atk < defender.def_:
            result["attacker_destroyed"] = True
            result["attacker_damage"] = defender.def_ - attacker.atk
    return result


def apply_battle_result(player_attacker, player_defender,
                        attacker_zone_idx: int,
                        defender_zone_idx: Optional[int],
                        result: dict) -> None:
    """
    应用战斗结果到游戏状态（修改 player 对象）
    defender_zone_idx: None 表示直接攻击
    """
    attacker_slot = player_attacker.field.monster_zones[attacker_zone_idx]
    if not attacker_slot:
        return
    attacker_slot["attacked_this_turn"] = True
    if result["attacker_destroyed"]:
        card = attacker_slot["card"]
        player_attacker.send_to_graveyard(card)
        player_attacker.field.monster_zones[attacker_zone_idx] = None
    if result["defender_destroyed"] and defender_zone_idx is not None:
        defender_slot = player_defender.field.monster_zones[defender_zone_idx]
        if defender_slot:
            card = defender_slot["card"]
            player_defender.send_to_graveyard(card)
            player_defender.field.monster_zones[defender_zone_idx] = None
    player_attacker.life_points -= result["attacker_damage"]
    player_defender.life_points -= result["defender_damage"]
