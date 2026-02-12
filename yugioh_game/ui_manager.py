"""
UI 绘制与鼠标事件处理
"""
import pygame
from .constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, CARD_WIDTH, CARD_HEIGHT,
    COLOR_FIELD, COLOR_BORDER, COLOR_CARD_BACK,
    PLAYER_HAND_Y, PLAYER_HAND_SPACING, BATTLE_LINE_Y,
    OPPONENT_HAND_Y, PLAYER_LP_X, PLAYER_LP_Y, OPPONENT_LP_X, OPPONENT_LP_Y,
    COLOR_WHITE, COLOR_LP_BG, COLOR_SELECTED, COLOR_HIGHLIGHT,
    PLAYER_MONSTER_CENTERS, PLAYER_MONSTER_Y,
)
from .card import Card


def draw_card_placeholder(surface: pygame.Surface, x: int, y: int,
                          card: Card = None, selected: bool = False,
                          show_back: bool = False, hover: bool = False) -> pygame.Rect:
    """
    绘制卡牌占位符
    x, y 为卡牌中心坐标
    """
    rect = pygame.Rect(
        x - CARD_WIDTH // 2,
        y - CARD_HEIGHT // 2,
        CARD_WIDTH,
        CARD_HEIGHT
    )
    border_width = 4 if selected else (3 if hover else 2)
    border_color = COLOR_SELECTED if selected else (COLOR_HIGHLIGHT if hover else COLOR_BORDER)
    color = COLOR_CARD_BACK if show_back else (card.get_display_color() if card else (128, 128, 128))
    pygame.draw.rect(surface, color, rect)
    pygame.draw.rect(surface, border_color, rect, border_width)
    return rect


def get_hand_card_rects(cards: list, x_start: int, y: int) -> list:
    """获取手牌每张卡的 rect 列表（用于点击检测）"""
    rects = []
    total_width = len(cards) * (CARD_WIDTH + PLAYER_HAND_SPACING) - PLAYER_HAND_SPACING
    start_x = x_start - total_width // 2 + CARD_WIDTH // 2
    for i in range(len(cards)):
        cx = start_x + i * (CARD_WIDTH + PLAYER_HAND_SPACING)
        rect = pygame.Rect(cx - CARD_WIDTH // 2, y - CARD_HEIGHT // 2, CARD_WIDTH, CARD_HEIGHT)
        rects.append(rect)
    return rects


def get_spell_trap_zone_rects(centers: list, y: int) -> list:
    """获取魔法陷阱区卡位 rect 列表"""
    return [
        pygame.Rect(cx - CARD_WIDTH // 2, y - CARD_HEIGHT // 2, CARD_WIDTH, CARD_HEIGHT)
        for cx in centers
    ]


def get_monster_zone_rects(centers: list, y: int) -> list:
    """获取怪兽区卡位 rect 列表"""
    return [
        pygame.Rect(cx - CARD_WIDTH // 2, y - CARD_HEIGHT // 2, CARD_WIDTH, CARD_HEIGHT)
        for cx in centers
    ]


def draw_field(surface: pygame.Surface):
    """绘制场地区域"""
    # 背景
    surface.fill(COLOR_FIELD)
    # 中央战斗线
    pygame.draw.line(surface, (0, 0, 0), (0, BATTLE_LINE_Y), (SCREEN_WIDTH, BATTLE_LINE_Y), 4)


def draw_hand(surface: pygame.Surface, cards: list, x_start: int, y: int,
              selected_index: int = -1, show_back: bool = False,
              hover_index: int = -1) -> list:
    """
    绘制手牌扇形展开
    返回每张卡的 rect 列表
    show_back: 对手手牌显示卡背
    """
    rects = []
    total_width = len(cards) * (CARD_WIDTH + PLAYER_HAND_SPACING) - PLAYER_HAND_SPACING
    start_x = x_start - total_width // 2 + CARD_WIDTH // 2
    for i, card in enumerate(cards):
        cx = start_x + i * (CARD_WIDTH + PLAYER_HAND_SPACING)
        rect = draw_card_placeholder(
            surface, cx, y, card,
            selected=(i == selected_index),
            show_back=show_back,
            hover=(i == hover_index)
        )
        rects.append(rect)
    return rects


def draw_spell_trap_zones(surface: pygame.Surface, slots: list, centers: list, y: int,
                         highlight_indices: list = None):
    """绘制魔法陷阱区"""
    highlight_indices = highlight_indices or []
    for i, cx in enumerate(centers):
        slot = slots[i] if i < len(slots) else None
        highlight = i in highlight_indices
        border_color = COLOR_HIGHLIGHT if highlight else COLOR_BORDER
        rect = pygame.Rect(cx - CARD_WIDTH // 2, y - CARD_HEIGHT // 2, CARD_WIDTH, CARD_HEIGHT)
        if slot:
            card = slot["card"]
            show_back = slot["position"] == "set"
            color = COLOR_CARD_BACK if show_back else card.get_display_color()
            pygame.draw.rect(surface, color, rect)
        else:
            pygame.draw.rect(surface, (50, 80, 50), rect)
        pygame.draw.rect(surface, border_color, rect, 4 if highlight else 2)


def draw_monster_zones(surface: pygame.Surface, monster_slots: list, centers: list, y: int,
                       highlight_indices: list = None, tribute_indices: list = None):
    """绘制怪兽区
    highlight_indices: 可放置/可选择的空位或怪兽
    tribute_indices: 已选为祭品的怪兽（金色边框）
    """
    from .card import Position
    highlight_indices = highlight_indices or []
    tribute_indices = tribute_indices or []
    for i, cx in enumerate(centers):
        slot = monster_slots[i] if i < len(monster_slots) else None
        highlight = i in highlight_indices
        is_tribute = i in tribute_indices
        if is_tribute:
            border_color = COLOR_SELECTED
        elif highlight:
            border_color = COLOR_HIGHLIGHT
        else:
            border_color = COLOR_BORDER
        rect = pygame.Rect(cx - CARD_WIDTH // 2, y - CARD_HEIGHT // 2, CARD_WIDTH, CARD_HEIGHT)
        if slot:
            card = slot["card"]
            color = card.get_display_color()
            show_back = slot["position"] == Position.SET
            pygame.draw.rect(surface, COLOR_CARD_BACK if show_back else color, rect)
        else:
            pygame.draw.rect(surface, (50, 80, 50), rect)
        pygame.draw.rect(surface, border_color, rect, 4 if highlight else 2)


def draw_attack_target_button(surface: pygame.Surface, x: int, y: int) -> pygame.Rect:
    """绘制直接攻击按钮"""
    font = pygame.font.Font(None, 28)
    rect = pygame.Rect(x - 60, y, 120, 36)
    pygame.draw.rect(surface, (180, 80, 80), rect)
    pygame.draw.rect(surface, COLOR_BORDER, rect, 2)
    text = font.render("直接攻击", True, COLOR_WHITE)
    tr = text.get_rect(center=rect.center)
    surface.blit(text, tr)
    return rect


def draw_position_buttons(surface: pygame.Surface, center_x: int, y: int) -> list:
    """绘制表示形式选择按钮，返回 (rect, position) 列表"""
    font = pygame.font.Font(None, 28)
    results = []
    labels = [("攻击表示", "attack"), ("守备表示", "defense"), ("里侧盖放", "set")]
    bw, bh = 100, 36
    total_w = len(labels) * (bw + 10) - 10
    start_x = center_x - total_w // 2
    for i, (label, pos) in enumerate(labels):
        rx = start_x + i * (bw + 10)
        rect = pygame.Rect(rx, y, bw, bh)
        pygame.draw.rect(surface, (80, 80, 80), rect)
        pygame.draw.rect(surface, COLOR_BORDER, rect, 2)
        text = font.render(label, True, COLOR_WHITE)
        tr = text.get_rect(center=rect.center)
        surface.blit(text, tr)
        results.append((rect, pos))
    return results


def draw_phase_button(surface: pygame.Surface, phase_name: str, x: int, y: int) -> pygame.Rect:
    """绘制下一阶段按钮"""
    font = pygame.font.Font(None, 24)
    rect = pygame.Rect(x, y, 120, 32)
    pygame.draw.rect(surface, (60, 60, 120), rect)
    pygame.draw.rect(surface, COLOR_BORDER, rect, 2)
    text = font.render(phase_name, True, COLOR_WHITE)
    tr = text.get_rect(center=rect.center)
    surface.blit(text, tr)
    return rect


def draw_life_points(surface: pygame.Surface, lp: int, x: int, y: int):
    """绘制生命值"""
    font = pygame.font.Font(None, 48)
    text = font.render(str(lp), True, COLOR_WHITE)
    rect = text.get_rect(center=(x, y))
    bg_rect = rect.inflate(20, 10)
    pygame.draw.rect(surface, COLOR_LP_BG, bg_rect)
    pygame.draw.rect(surface, COLOR_BORDER, bg_rect, 2)
    surface.blit(text, rect)
