"""
游戏入口：主循环、事件分发、阶段切换
"""
import pygame
import sys
from .constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, PLAYER_HAND_Y, OPPONENT_HAND_Y,
    PLAYER_LP_X, PLAYER_LP_Y, OPPONENT_LP_X, OPPONENT_LP_Y,
    PLAYER_MONSTER_CENTERS, PLAYER_MONSTER_Y, OPPONENT_MONSTER_Y,
    PLAYER_SPELL_CENTERS, PLAYER_SPELL_Y, OPPONENT_SPELL_Y,
)
from .game_state import init_game_state
from .card import Position
from .constants import PHASE_NAMES
from .ui_manager import (
    draw_field, draw_hand, draw_life_points, draw_monster_zones,
    draw_spell_trap_zones,
    draw_position_buttons, draw_attack_target_button, draw_phase_button,
    get_hand_card_rects, get_monster_zone_rects, get_spell_trap_zone_rects,
)


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("游戏王 - Pygame")
    clock = pygame.time.Clock()

    state = init_game_state()
    from .game_state import set_phase_for_testing
    set_phase_for_testing(state, "draw")  # 从抽卡阶段开始
    selected_index = -1
    hover_hand_index = -1
    dragging_index = -1
    drag_pos = None
    highlight_zones = []
    spell_highlight = []

    op_mode = "idle"
    pending_summon = None
    selected_tributes = []
    position_buttons = []
    pending_attack = None
    direct_attack_rect = None

    running = True
    while running:
        if state.game_over:
            font = pygame.font.Font(None, 72)
            if state.winner == "player1":
                text = font.render("你赢了！", True, (255, 215, 0))
            else:
                text = font.render("你输了！", True, (255, 100, 100))
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            draw_field(screen)
            screen.blit(text, rect)
            pygame.display.flip()
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    running = False
            clock.tick(FPS)
            continue
        mouse_pos = pygame.mouse.get_pos()
        hand_center_x = SCREEN_WIDTH // 2

        player_hand_rects = get_hand_card_rects(state.player1.hand, hand_center_x, PLAYER_HAND_Y)
        monster_zone_rects = get_monster_zone_rects(PLAYER_MONSTER_CENTERS, PLAYER_MONSTER_Y)
        spell_trap_zone_rects = get_spell_trap_zone_rects(PLAYER_SPELL_CENTERS, PLAYER_SPELL_Y)
        opponent_monster_rects = get_monster_zone_rects(PLAYER_MONSTER_CENTERS, OPPONENT_MONSTER_Y)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if op_mode != "idle":
                        op_mode = "idle"
                        pending_summon = None
                        pending_attack = None
                        selected_tributes = []
                        selected_index = -1
                    else:
                        running = False
                    dragging_index = -1

            elif event.type == pygame.MOUSEMOTION:
                if dragging_index >= 0:
                    drag_pos = mouse_pos
                    highlight_zones = []
                    spell_highlight.clear()
                    if dragging_index < len(state.player1.hand):
                        card = state.player1.hand[dragging_index]
                        if card.is_monster():
                            for i in range(len(monster_zone_rects)):
                                if state.player1.field.monster_zones[i] is None:
                                    highlight_zones.append(i)
                        elif card.is_spell() or card.is_trap():
                            for i in range(5):
                                if state.player1.field.spell_trap_zones[i] is None:
                                    spell_highlight.append(i)
                else:
                    hover_hand_index = -1
                    for i, rect in enumerate(player_hand_rects):
                        if rect.collidepoint(mouse_pos):
                            hover_hand_index = i
                            break

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if op_mode == "idle":
                        phase_btn = pygame.Rect(SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT - 40, 120, 32)
                        if phase_btn.collidepoint(mouse_pos):
                            from .phase_logic import advance_phase
                            advance_phase(state)
                            continue
                    if op_mode == "select_attack_target":
                        from .battle import calc_battle, apply_battle_result
                        from .card import Position
                        if pending_attack is not None:
                            aidx = pending_attack["attacker_zone_idx"]
                            slot = state.player1.field.monster_zones[aidx]
                            if slot and slot["position"] == Position.ATTACK and not slot["attacked_this_turn"]:
                                opponent_has_monsters = any(state.player2.field.monster_zones)
                                for i, rect in enumerate(opponent_monster_rects):
                                    if rect.collidepoint(mouse_pos):
                                        def_slot = state.player2.field.monster_zones[i]
                                        if def_slot:
                                            res = calc_battle(slot["card"], slot["position"], def_slot)
                                            if res.get("flip_defender"):
                                                state.player2.field.monster_zones[i]["position"] = Position.DEFENSE
                                            apply_battle_result(
                                                state.player1, state.player2,
                                                aidx, i, res
                                            )
                                            op_mode = "idle"
                                            pending_attack = None
                                            break
                                if op_mode == "select_attack_target" and direct_attack_rect and direct_attack_rect.collidepoint(mouse_pos) and not opponent_has_monsters:
                                    res = calc_battle(slot["card"], slot["position"], None)
                                    apply_battle_result(state.player1, state.player2, aidx, None, res)
                                    op_mode = "idle"
                                    pending_attack = None
                        break
                    elif op_mode == "select_tribute":
                        for i, rect in enumerate(monster_zone_rects):
                            if rect.collidepoint(mouse_pos) and pending_summon:
                                needed = state.player1.get_tribute_count(
                                    state.player1.hand[pending_summon["hand_index"]].level
                                )
                                slot = state.player1.field.monster_zones[i]
                                if slot and i not in selected_tributes:
                                    selected_tributes.append(i)
                                    if len(selected_tributes) >= needed:
                                        pending_summon["tribute_indices"] = list(selected_tributes)
                                        op_mode = "select_position"
                                        break
                                elif i in selected_tributes:
                                    selected_tributes.remove(i)
                        break
                    elif op_mode == "select_position":
                        for rect, pos in position_buttons:
                            if rect.collidepoint(mouse_pos) and pending_summon:
                                state.player1.summon_monster(
                                    pending_summon["hand_index"],
                                    pending_summon["zone_index"],
                                    pos,
                                    pending_summon.get("tribute_indices", selected_tributes)
                                )
                                state.normal_summoned_this_turn = True
                                op_mode = "idle"
                                pending_summon = None
                                selected_tributes = []
                                selected_index = -1
                        break
                    elif dragging_index >= 0:
                        pass
                    elif op_mode == "idle" and state.current_player == "player1" and state.current_phase == "battle":
                        for i, rect in enumerate(monster_zone_rects):
                            if rect.collidepoint(mouse_pos):
                                slot = state.player1.field.monster_zones[i]
                                if slot and slot["position"] == Position.ATTACK and not slot["attacked_this_turn"]:
                                    op_mode = "select_attack_target"
                                    pending_attack = {"attacker_zone_idx": i}
                                break
                    else:
                        for i, rect in enumerate(player_hand_rects):
                            if rect.collidepoint(mouse_pos):
                                if selected_index == i:
                                    selected_index = -1
                                else:
                                    selected_index = i
                                    dragging_index = i
                                    drag_pos = mouse_pos
                                break
                        else:
                            selected_index = -1

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and dragging_index >= 0 and op_mode == "idle":
                    hand_idx = dragging_index
                    card = state.player1.hand[hand_idx] if hand_idx < len(state.player1.hand) else None
                    placed_spell_trap = False
                    for i, rect in enumerate(spell_trap_zone_rects):
                        if rect.collidepoint(mouse_pos) and i in spell_highlight and card and (card.is_spell() or card.is_trap()):
                            if state.current_player == "player1" and state.current_phase in ("main1", "main2"):
                                if card.is_spell() and card.subtype == "normal":
                                    from .effects import effect_pot_of_greed, effect_dark_hole, effect_monster_reborn
                                    base_id = card.card_id.split("_")[0] if "_" in card.card_id else card.card_id
                                    state.player1.hand.pop(hand_idx)
                                    state.player1.send_to_graveyard(card)
                                    if base_id == "s001":
                                        effect_pot_of_greed(state, "player1")
                                    elif base_id == "s002":
                                        if state.player1.get_graveyard_monsters() or state.player2.get_graveyard_monsters():
                                            effect_monster_reborn(state, "player1", 0)
                                    elif base_id == "s003":
                                        effect_dark_hole(state)
                                    placed_spell_trap = True
                                    break
                                elif card.is_trap():
                                    state.player1.set_spell_trap(hand_idx, i, False, state.turn_count)
                                    placed_spell_trap = True
                                    break
                    if not placed_spell_trap:
                        for i, rect in enumerate(monster_zone_rects):
                            if rect.collidepoint(mouse_pos) and i in highlight_zones:
                                if (state.current_player == "player1" and state.current_phase in ("main1", "main2")
                                        and not state.normal_summoned_this_turn):
                                    card = state.player1.hand[dragging_index]
                                    if card and card.is_monster():
                                        needed = state.player1.get_tribute_count(card.level)
                                        if needed == 0:
                                            op_mode = "select_position"
                                            pending_summon = {
                                                "hand_index": dragging_index,
                                                "zone_index": i,
                                                "tribute_indices": [],
                                            }
                                        else:
                                            op_mode = "select_tribute"
                                            pending_summon = {
                                                "hand_index": dragging_index,
                                                "zone_index": i,
                                                "tribute_indices": [],
                                            }
                                            selected_tributes = []
                                        selected_index = -1
                                        break
                    dragging_index = -1
                    drag_pos = None
                    highlight_zones = []
                    spell_highlight.clear()
                    if op_mode == "idle" and not pending_summon:
                        selected_index = -1 if placed_spell_trap else hand_idx

        # 绘制
        draw_field(screen)

        # 对手区域
        draw_hand(screen, state.player2.hand, hand_center_x, OPPONENT_HAND_Y, show_back=True)
        opp_hl = [i for i in range(5) if state.player2.field.monster_zones[i]] if op_mode == "select_attack_target" else []
        draw_monster_zones(screen, state.player2.field.monster_zones,
                           PLAYER_MONSTER_CENTERS, OPPONENT_MONSTER_Y,
                           highlight_indices=opp_hl)
        draw_spell_trap_zones(screen, state.player2.field.spell_trap_zones,
                              PLAYER_SPELL_CENTERS, OPPONENT_SPELL_Y)
        draw_spell_trap_zones(screen, state.player1.field.spell_trap_zones,
                              PLAYER_SPELL_CENTERS, PLAYER_SPELL_Y,
                              highlight_indices=spell_highlight if dragging_index >= 0 else [])

        # 玩家怪兽区
        monster_hl = highlight_zones if dragging_index >= 0 else []
        if op_mode == "select_tribute":
            monster_hl = [i for i in range(5) if state.player1.field.monster_zones[i]]
        draw_monster_zones(screen, state.player1.field.monster_zones,
                           PLAYER_MONSTER_CENTERS, PLAYER_MONSTER_Y,
                           highlight_indices=monster_hl,
                           tribute_indices=selected_tributes)

        # 玩家手牌
        draw_hand(screen, state.player1.hand, hand_center_x, PLAYER_HAND_Y,
                  selected_index,
                  hover_index=hover_hand_index if dragging_index < 0 else -1)

        if dragging_index >= 0 and dragging_index < len(state.player1.hand) and drag_pos:
            from .ui_manager import draw_card_placeholder
            draw_card_placeholder(screen, drag_pos[0], drag_pos[1],
                                  state.player1.hand[dragging_index], selected=True)

        # 表示形式选择
        if op_mode == "select_position":
            position_buttons = draw_position_buttons(screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)

        # 攻击目标选择：直接攻击按钮
        if op_mode == "select_attack_target":
            opponent_has_monsters = any(state.player2.field.monster_zones)
            if not opponent_has_monsters:
                direct_attack_rect = draw_attack_target_button(
                    screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20
                )
            else:
                direct_attack_rect = None

        # 祭品选择提示
        if op_mode == "select_tribute" and pending_summon:
            font = pygame.font.Font(None, 32)
            needed = state.player1.get_tribute_count(
                state.player1.hand[pending_summon["hand_index"]].level
            )
            text = font.render(f"选择 {needed} 只怪兽作为祭品 (ESC 取消)", True, (255, 255, 255))
            screen.blit(text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 80))

        draw_life_points(screen, state.player2.life_points, OPPONENT_LP_X, OPPONENT_LP_Y)
        draw_life_points(screen, state.player1.life_points, PLAYER_LP_X, PLAYER_LP_Y)

        if state.player1.life_points <= 0:
            state.game_over = True
            state.winner = "player2"
        elif state.player2.life_points <= 0:
            state.game_over = True
            state.winner = "player1"
        elif state.current_phase == "draw" and state.current_player == "player1" and not state.player1.can_draw():
            state.game_over = True
            state.winner = "player2"
        elif state.current_phase == "draw" and state.current_player == "player2" and not state.player2.can_draw():
            state.game_over = True
            state.winner = "player1"

        phase_btn = draw_phase_button(
            screen, "下一阶段",
            SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT - 40
        )
        phase_txt = PHASE_NAMES.get(state.current_phase, state.current_phase)
        font = pygame.font.Font(None, 28)
        t = font.render(phase_txt, True, (255, 255, 255))
        screen.blit(t, (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT - 90))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
