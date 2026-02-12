"""
卡牌数据库：30张基础卡 + 效果注册
含：青眼白龙、黑魔导、死者苏生、强欲之壶、圣防护罩等
"""
import copy
import random
from typing import Callable, Dict, Any
from .card import Card


def _create_monster(card_id: str, name: str, level: int, atk: int, def_: int,
                    attribute: str, race: str, subtype: str = "normal",
                    effect_text: str = "") -> dict:
    return {
        "card_id": card_id,
        "name": name,
        "card_type": "monster",
        "subtype": subtype,
        "effect_text": effect_text,
        "effect_function": None,
        "level": level,
        "atk": atk,
        "def_": def_,
        "attribute": attribute,
        "race": race,
    }


def _create_spell(card_id: str, name: str, effect_text: str,
                  subtype: str = "normal",
                  effect_function: Callable = None) -> dict:
    return {
        "card_id": card_id,
        "name": name,
        "card_type": "spell",
        "subtype": subtype,
        "effect_text": effect_text,
        "effect_function": effect_function,
        "level": 0,
        "atk": 0,
        "def_": 0,
        "attribute": "",
        "race": "",
    }


def _create_trap(card_id: str, name: str, effect_text: str,
                 subtype: str = "normal",
                 effect_function: Callable = None) -> dict:
    return {
        "card_id": card_id,
        "name": name,
        "card_type": "trap",
        "subtype": subtype,
        "effect_text": effect_text,
        "effect_function": effect_function,
        "level": 0,
        "atk": 0,
        "def_": 0,
        "attribute": "",
        "race": "",
    }


# 效果函数将在 game_state 引入后实现
CARD_TEMPLATES: Dict[str, dict] = {}

# 怪兽卡 20张
MONSTER_TEMPLATES = [
    _create_monster("m001", "青眼白龙", 8, 3000, 2500, "光", "龙族", "normal", "以高攻击力著称的传说之龙。"),
    _create_monster("m002", "黑魔导", 7, 2500, 2100, "暗", "魔法师族", "normal", "魔法师族中最强的魔法师。"),
    _create_monster("m003", "真红眼黑龙", 7, 2400, 2000, "暗", "龙族", "normal", "愤怒的黑龙，其黑炎可将一切烧尽。"),
    _create_monster("m004", "暗黑骑士盖亚", 7, 2300, 2100, "地", "战士族", "normal", "持枪的黑暗骑士。"),
    _create_monster("m005", "混沌战士", 8, 3000, 2500, "光", "战士族", "normal", "传说中最强的战士。"),
    _create_monster("m006", "破龙剑士", 7, 2600, 2300, "地", "战士族", "normal", "屠龙之剑的持有者。"),
    _create_monster("m007", "精灵剑士", 4, 1400, 1200, "地", "战士族", "normal", "灵活运用剑术的精灵战士。"),
    _create_monster("m008", "雷龙", 5, 1600, 1500, "光", "雷族", "normal", "放出雷电的龙。"),
    _create_monster("m009", "栗子球", 1, 300, 200, "暗", "恶魔族", "effect", "从手牌丢弃此卡，可抵御一次战斗伤害。"),
    _create_monster("m010", "岩石巨兵", 3, 1300, 2000, "地", "岩石族", "normal", "由岩石构成的巨人。"),
    _create_monster("m011", "牛头人", 4, 1700, 1000, "地", "兽战士族", "normal", "半人半牛的怪物。"),
    _create_monster("m012", "诅咒之龙", 5, 2000, 1500, "暗", "龙族", "normal", "被诅咒的龙。"),
    _create_monster("m013", "蓝宝石龙", 4, 1900, 1600, "风", "龙族", "normal", "蓝宝石般闪耀的龙。"),
    _create_monster("m014", "恶魔召唤", 6, 2500, 1200, "暗", "恶魔族", "normal", "使用雷电的恶魔。"),
    _create_monster("m015", "炎之剑士", 5, 1800, 1600, "炎", "战士族", "normal", "挥舞炎之剑的战士。"),
    _create_monster("m016", "地割", 4, 1200, 1500, "地", "兽族", "normal", "从地底出现的怪兽。"),
    _create_monster("m017", "水龙", 5, 1800, 1600, "水", "海龙族", "normal", "栖息于深海的龙。"),
    _create_monster("m018", "双头雷龙", 7, 2800, 2100, "光", "雷族", "normal", "拥有两个头的雷龙。"),
    _create_monster("m019", "黑魔导女孩", 6, 2000, 1700, "暗", "魔法师族", "normal", "黒魔导的弟子。"),
    _create_monster("m020", "圣精灵", 4, 800, 2000, "光", "魔法师族", "normal", "守护自然的精灵。"),
]

# 魔法卡 5张
SPELL_TEMPLATES = [
    _create_spell("s001", "强欲之壶", "抽2张卡。", "normal"),
    _create_spell("s002", "死者苏生", "从任意玩家墓地特殊召唤1只怪兽。", "normal"),
    _create_spell("s003", "黑洞", "破坏场上所有怪兽。", "normal"),
    _create_spell("s004", "闪电漩涡", "丢弃1张手牌，破坏对手场上所有表侧怪兽。", "normal"),
    _create_spell("s005", "大风暴", "破坏场上所有魔法陷阱卡。", "normal"),
]

# 陷阱卡 5张
TRAP_TEMPLATES = [
    _create_trap("t001", "圣防护罩 -镜之力-", "对手怪兽攻击宣言时，破坏对手所有攻击表示怪兽。", "normal"),
    _create_trap("t002", "激流葬", "怪兽召唤、反转召唤、特殊召唤时，破坏场上所有怪兽。", "normal"),
    _create_trap("t003", "圣光防护罩", "对手宣言直接攻击时，对手怪兽全部破坏。", "normal"),
    _create_trap("t004", "魔法筒", "对手怪兽攻击宣言时，将1只攻击怪兽的攻击无效，给予对手其攻击力数值的伤害。", "counter"),
    _create_trap("t005", "落穴", "对手召唤攻击力1000以上的怪兽时，破坏那只怪兽。", "normal"),
]

# 合并模板
for t in MONSTER_TEMPLATES + SPELL_TEMPLATES + TRAP_TEMPLATES:
    CARD_TEMPLATES[t["card_id"]] = t


def create_card_from_template(temp_id: str, instance_id: str = None) -> Card:
    """从模板创建卡牌实例"""
    if temp_id not in CARD_TEMPLATES:
        raise ValueError(f"Unknown card template: {temp_id}")
    t = CARD_TEMPLATES[temp_id]
    card_id = f"{temp_id}_{instance_id}" if instance_id else temp_id
    return Card(
        card_id=card_id,
        name=t["name"],
        card_type=t["card_type"],
        subtype=t["subtype"],
        effect_text=t.get("effect_text", ""),
        effect_function=t.get("effect_function"),
        level=t.get("level", 1),
        atk=t.get("atk", 0),
        def_=t.get("def_", 0),
        attribute=t.get("attribute", ""),
        race=t.get("race", ""),
    )


def create_starter_deck() -> list:
    """创建40张初始卡组（20怪兽+10魔法+10陷阱）"""
    import uuid
    monster_ids = [t["card_id"] for t in MONSTER_TEMPLATES]
    spell_ids = [t["card_id"] for t in SPELL_TEMPLATES]
    trap_ids = [t["card_id"] for t in TRAP_TEMPLATES]
    deck_temps = (
        random.choices(monster_ids, k=20) +
        random.choices(spell_ids, k=10) +
        random.choices(trap_ids, k=10)
    )
    random.shuffle(deck_temps)
    return [create_card_from_template(tid, str(uuid.uuid4())[:8]) for tid in deck_temps]


def create_random_deck() -> list:
    """创建随机40张卡组"""
    import uuid
    temp_ids = list(CARD_TEMPLATES.keys())
    # 确保约20怪兽、10魔法、10陷阱
    monster_ids = [k for k in temp_ids if CARD_TEMPLATES[k]["card_type"] == "monster"]
    spell_ids = [k for k in temp_ids if CARD_TEMPLATES[k]["card_type"] == "spell"]
    trap_ids = [k for k in temp_ids if CARD_TEMPLATES[k]["card_type"] == "trap"]
    deck_temps = []
    deck_temps.extend(random.choices(monster_ids, k=20))
    deck_temps.extend(random.choices(spell_ids, k=10))
    deck_temps.extend(random.choices(trap_ids, k=10))
    random.shuffle(deck_temps)
    return [create_card_from_template(tid, str(uuid.uuid4())[:8]) for tid in deck_temps]
