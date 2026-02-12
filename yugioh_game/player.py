"""
Player 类：卡组、手牌、墓地、生命值、操作接口
"""
import random
from typing import List, Optional
from .card import Card
from .field import Field, create_monster_slot, create_spell_trap_slot, Position


INITIAL_LP = 8000


class Player:
    def __init__(self, player_id: str, deck: List[Card]):
        self.player_id = player_id
        self.deck = list(deck)
        self.hand: List[Card] = []
        self.graveyard: List[Card] = []
        self.extra_deck: List[Card] = []
        self.life_points = INITIAL_LP
        self.field = Field()

    def shuffle_deck(self):
        """洗牌"""
        random.shuffle(self.deck)

    def draw(self, count: int = 1) -> List[Card]:
        """从卡组抽卡，返回抽到的卡列表"""
        drawn = []
        for _ in range(count):
            if not self.deck:
                break
            card = self.deck.pop(0)
            self.hand.append(card)
            drawn.append(card)
        return drawn

    def can_draw(self) -> bool:
        """是否还能抽卡"""
        return len(self.deck) > 0

    def send_to_graveyard(self, card: Card):
        """将卡送入墓地"""
        self.graveyard.append(card)

    def get_graveyard_monsters(self) -> List[Card]:
        """墓地中的怪兽卡"""
        return [c for c in self.graveyard if c.is_monster()]

    def set_spell_trap(self, hand_index: int, zone_index: int, face_up: bool, set_turn: int) -> bool:
        """盖放或发动魔法陷阱到魔法陷阱区"""
        if hand_index < 0 or hand_index >= len(self.hand):
            return False
        card = self.hand[hand_index]
        if not (card.is_spell() or card.is_trap()):
            return False
        if zone_index < 0 or zone_index >= 5:
            return False
        if self.field.spell_trap_zones[zone_index] is not None:
            return False
        self.hand.pop(hand_index)
        pos = "face_up" if face_up else "set"
        self.field.spell_trap_zones[zone_index] = create_spell_trap_slot(card, pos, set_turn)
        return True

    def get_tribute_count(self, level: int) -> int:
        """根据等级返回需要的祭品数量"""
        if level <= 4:
            return 0
        elif level <= 6:
            return 1
        else:
            return 2

    def summon_monster(self, hand_index: int, zone_index: int, position: str,
                       tribute_indices: List[int] = None) -> bool:
        """
        召唤：从手牌将怪兽放到怪兽区
        tribute_indices: 祭品怪兽的场地区域索引列表
        position: "attack" | "defense" | "set"
        """
        tribute_indices = tribute_indices or []
        if hand_index < 0 or hand_index >= len(self.hand):
            return False
        card = self.hand[hand_index]
        if not card.is_monster():
            return False
        if zone_index < 0 or zone_index >= 5:
            return False
        if self.field.monster_zones[zone_index] is not None:
            return False
        needed = self.get_tribute_count(card.level)
        if needed != len(tribute_indices):
            return False
        if needed > 0:
            for ti in tribute_indices:
                if ti < 0 or ti >= 5 or ti == zone_index:
                    return False
                if self.field.monster_zones[ti] is None:
                    return False
        self.hand.pop(hand_index)
        for ti in sorted(tribute_indices, reverse=True):
            slot = self.field.monster_zones[ti]
            self.send_to_graveyard(slot["card"])
            self.field.monster_zones[ti] = None
        self.field.monster_zones[zone_index] = create_monster_slot(
            card, position, summoned_this_turn=True
        )
        return True
