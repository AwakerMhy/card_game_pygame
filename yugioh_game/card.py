"""
Card 类定义：卡牌数据结构、表示形式枚举
"""
from dataclasses import dataclass, field
from typing import Optional, Callable, Any


# 表示形式
class Position:
    """怪兽表示形式"""
    ATTACK = "attack"      # 表侧攻击
    DEFENSE = "defense"    # 表侧守备
    SET = "set"            # 里侧守备


@dataclass
class Card:
    """卡牌数据类"""
    card_id: str
    name: str
    card_type: str          # "monster" | "spell" | "trap"
    subtype: str
    effect_text: str = ""
    effect_function: Optional[Callable] = None

    # 怪兽特有属性
    level: int = 1
    atk: int = 0
    def_: int = 0
    attribute: str = ""
    race: str = ""

    def is_monster(self) -> bool:
        return self.card_type == "monster"

    def is_spell(self) -> bool:
        return self.card_type == "spell"

    def is_trap(self) -> bool:
        return self.card_type == "trap"

    def get_display_color(self) -> tuple:
        """获取卡牌显示颜色"""
        if self.card_type == "monster":
            return (255, 139, 83)   # 橙色
        elif self.card_type == "spell":
            return (29, 158, 116)   # 绿色
        elif self.card_type == "trap":
            return (188, 90, 132)   # 紫色
        return (128, 128, 128)

    def copy(self) -> "Card":
        """创建卡牌副本"""
        return Card(
            card_id=self.card_id,
            name=self.name,
            card_type=self.card_type,
            subtype=self.subtype,
            effect_text=self.effect_text,
            effect_function=self.effect_function,
            level=self.level,
            atk=self.atk,
            def_=self.def_,
            attribute=self.attribute,
            race=self.race,
        )
