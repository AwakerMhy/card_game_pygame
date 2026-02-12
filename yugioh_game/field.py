"""
Field 类：怪兽区/魔法陷阱区 5 卡位管理
"""
from typing import Optional, List
from .card import Card, Position


# 怪兽区卡位
MonsterSlot = Optional[dict]  # None=空; 否则包含 card, position, attacked_this_turn 等


def create_empty_monster_slot() -> None:
    return None


def create_monster_slot(card: Card, position: str,
                       attacked_this_turn: bool = False,
                       changed_position_this_turn: bool = False,
                       summoned_this_turn: bool = False) -> dict:
    return {
        "card": card,
        "position": position,
        "attacked_this_turn": attacked_this_turn,
        "changed_position_this_turn": changed_position_this_turn,
        "summoned_this_turn": summoned_this_turn,
    }


def create_empty_spell_trap_slot() -> None:
    return None


def create_spell_trap_slot(card: Card, position: str, set_turn: int = 0) -> dict:
    return {
        "card": card,
        "position": position,  # "face_up" | "set"
        "set_turn": set_turn,
    }


class Field:
    """玩家场地：怪兽区5格 + 魔法陷阱区5格"""

    def __init__(self):
        self.monster_zones: List[MonsterSlot] = [None] * 5
        self.spell_trap_zones: List[Optional[dict]] = [None] * 5

    def get_empty_monster_index(self) -> Optional[int]:
        for i, slot in enumerate(self.monster_zones):
            if slot is None:
                return i
        return None

    def get_empty_spell_trap_index(self) -> Optional[int]:
        for i, slot in enumerate(self.spell_trap_zones):
            if slot is None:
                return i
        return None

    def get_attack_position_monsters(self) -> List[tuple]:
        """返回 (index, slot) 列表，表侧攻击表示的怪兽"""
        result = []
        for i, slot in enumerate(self.monster_zones):
            if slot and slot["position"] == Position.ATTACK and not slot["attacked_this_turn"]:
                result.append((i, slot))
        return result

    def get_all_monsters(self) -> List[tuple]:
        """返回 (index, slot) 列表"""
        return [(i, s) for i, s in enumerate(self.monster_zones) if s]

    def get_face_up_monsters(self) -> List[tuple]:
        """返回表侧怪兽 (index, slot)"""
        return [(i, s) for i, s in enumerate(self.monster_zones) if s and s["position"] != Position.SET]
