# -*- coding: big5 -*-
import pygame
import random

# 初始化
pygame.init()
pygame.font.init()

# 字體設定
ch_font = pygame.font.Font("msjh.ttc", 36)
font = pygame.font.Font(None, 36)

# 螢幕設定
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Investigative RPG - Battle Scene")

# 顏色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 0, 0)
GREEN = (0, 200, 0)
BLUE = (0, 100, 200)
GOLD = (255, 215, 0)
LIGHT_BLUE = (100, 180, 255)

# 圖片
battle_bg = pygame.image.load("battle_bg.jpg")
victory_bg = pygame.image.load("victory_bg.jpg")
defeat_bg = pygame.image.load("defeat_bg.jpg")
map_bg = pygame.transform.scale(pygame.image.load("map_bg.jpg"), (WIDTH, HEIGHT))
player_small_img = pygame.transform.scale(pygame.image.load("player_small.jpg"), (64, 64))
player_battle_img = pygame.transform.scale(pygame.image.load("player.png"), (200, 200))
player_intro_img = pygame.transform.scale(pygame.image.load("player_inter.png"), (200, 200))
enemy_img = pygame.transform.scale(pygame.image.load("enemy.jpg"), (64, 64))
enemy_battle_img = pygame.transform.scale(pygame.image.load("enemy.jpg"), (200, 200))
exit_img = pygame.transform.scale(pygame.image.load("exit_wood.png"), (100, 100))
intro_bg = pygame.transform.scale(pygame.image.load("first_substitute_bg.jpg"), (WIDTH, HEIGHT))

# 出口區域與閃爍提示
exit_rect = pygame.Rect(1000, 700, 100, 100)
flash_timer = 0

# 角色類別
class Character:
    def __init__(self, name, hp, attack, weakness, image, pos):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.attack = attack
        self.weakness = weakness
        self.image = image
        self.pos = pos
        self.damage_history = []
        self.buffed = False

    def take_damage(self, damage, skill_name="Unknown Attack"):
        self.hp = max(0, self.hp - damage)
        self.damage_history.append(f"{skill_name}: {damage} dmg")

    def heal(self, amount):
        self.hp = min(self.max_hp, self.hp + amount)

# 地圖敵人
def get_map_enemies():
    return [
        Character("黑蛇首領", 80, 15, "火", enemy_img, [400, 300]),
        Character("暗影刺客", 90, 20, "雷", enemy_img, [700, 500]),
    ]

# 重設遊戲
def reset_game():
    global player, map_enemies, enemy, game_state, battle_prompt, next_turn_buff, move_keys, show_intro_button
    player = Character("山村真紀", 100, 20, None, player_small_img, [100, 100])
    player.battle_image = player_battle_img
    map_enemies = get_map_enemies()
    enemy = None
    battle_prompt = None
    next_turn_buff = False
    game_state = "intro_image"
    move_keys = {pygame.K_UP: False, pygame.K_DOWN: False, pygame.K_LEFT: False, pygame.K_RIGHT: False}
    show_intro_button = True

reset_game()

skills = [
    {"text": "審問打擊", "damage": 20, "element": "火", "rect": pygame.Rect(250, 650, 200, 50)},
    {"text": "監視之眼", "damage": 0, "element": "無", "rect": pygame.Rect(500, 650, 200, 50)},
    {"text": "精準制伏", "damage": 30, "element": "無", "rect": pygame.Rect(750, 650, 200, 50)}
]

def draw_health_bar(character, x, y):
    bar_width = 240
    bar_height = 20
    hp_ratio = character.hp / character.max_hp
    pygame.draw.rect(screen, RED, (x, y, bar_width, bar_height))
    pygame.draw.rect(screen, GREEN, (x, y, int(bar_width * hp_ratio), bar_height))
    hp_text = font.render(f"{character.hp}/{character.max_hp}", True, WHITE)
    screen.blit(hp_text, (x + 90, y))

def draw_character_info(character, x, y):
    name_text = ch_font.render(character.name, True, WHITE)
    screen.blit(name_text, (x, y))

clock = pygame.time.Clock()
running = True
while running:
    dt = clock.tick(60)
    screen.fill(BLACK)
    flash_timer += 1
    mouse_pos = pygame.mouse.get_pos()

    # === 遊戲開始畫面（圖片選角） ===
    if game_state == "intro_image":
        intro_rect = player_intro_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        hover = intro_rect.collidepoint(mouse_pos)
        scale = 1.05 if hover else 1.0
        w, h = player_intro_img.get_size()
        scaled_img = pygame.transform.smoothscale(player_intro_img, (int(w * scale), int(h * scale)))
        scaled_rect = scaled_img.get_rect(center=intro_rect.center)
        screen.blit(scaled_img, scaled_rect.topleft)
        intro_button_rect = scaled_rect  # 圖片作為按鈕

    # === 介紹畫面 ===
    elif game_state == "intro":
        screen.blit(intro_bg, (0, 0))
        panel_surface = pygame.Surface((800, 400))
        panel_surface.set_alpha(180)
        panel_surface.fill((0, 0, 0))
        screen.blit(panel_surface, (200, 80))

        intro_text = [
            "頂尖搜查官：山村真紀小姐",
            "政府直屬組織",
            "特殊麻藥調查局的搜查官",
            "頭腦清晰",
            "格鬥與射擊技術超一流",
            "在局內大家都稱她為“冰之女”……"
        ]
        for i, line in enumerate(intro_text):
            text_surface = ch_font.render(line, True, WHITE)
            text_rect = text_surface.get_rect(center=(WIDTH // 2, 120 + i * 50))
            screen.blit(text_surface, text_rect.topleft)

        button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 100, 200, 50)
        pygame.draw.rect(screen, WHITE, button_rect, border_radius=10)
        pygame.draw.rect(screen, (200, 200, 200), button_rect, 3, border_radius=10)
        button_text = ch_font.render("下一步", True, BLACK)
        text_rect = button_text.get_rect(center=button_rect.center)
        screen.blit(button_text, text_rect.topleft)

    # === 地圖階段 ===
    elif game_state == "map":
        screen.blit(map_bg, (0, 0))
        screen.blit(player.image, player.pos)
        for m in map_enemies:
            screen.blit(m.image, m.pos)

        if battle_prompt:
            prompt_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT - 100, 300, 60)
            pygame.draw.rect(screen, BLUE, prompt_rect, border_radius=10)
            prompt_text = ch_font.render("敵人出現！點擊進入戰鬥", True, WHITE)
            text_rect = prompt_text.get_rect(center=prompt_rect.center)
            screen.blit(prompt_text, text_rect.topleft)

        if not map_enemies:
            screen.blit(exit_img, exit_rect.topleft)
            if flash_timer % 60 < 30:
                exit_tip = ch_font.render("出口 →", True, GOLD)
                screen.blit(exit_tip, (exit_rect.x - 100, exit_rect.y - 20))

            if exit_rect.collidepoint(player.pos[0] + 32, player.pos[1] + 32):
                game_state = "victory"

        if move_keys[pygame.K_UP]: player.pos[1] -= 2
        if move_keys[pygame.K_DOWN]: player.pos[1] += 2
        if move_keys[pygame.K_LEFT]: player.pos[0] -= 2
        if move_keys[pygame.K_RIGHT]: player.pos[0] += 2

    # === 戰鬥階段 ===
    elif game_state == "battle":
        screen.blit(battle_bg, (0, 0))
        draw_character_info(player, 10, 10)
        draw_character_info(enemy, WIDTH - 250, 10)
        screen.blit(player.battle_image, (100, 200))
        screen.blit(enemy_battle_img, (WIDTH - 400, 200))
        draw_health_bar(player, 10, 50)
        draw_health_bar(enemy, WIDTH - 250, 50)

        weakness_text = ch_font.render(f"敵人弱點: {enemy.weakness}", True, RED)
        screen.blit(weakness_text, (WIDTH - 350, 180))

        for skill in skills:
            color = GOLD if skill["rect"].collidepoint(mouse_pos) else BLUE
            pygame.draw.rect(screen, color, skill["rect"], border_radius=20)
            text_surf = ch_font.render(skill["text"], True, WHITE)
            screen.blit(text_surf, (skill["rect"].x + 10, skill["rect"].y + 10))

        if player.damage_history:
            last_skill = player.damage_history[-1]
            log_text = ch_font.render(f"你使用了 {last_skill}", True, WHITE)
            screen.blit(log_text, (50, HEIGHT - 100))

    # === 勝利畫面 ===
    elif game_state == "victory":
        screen.blit(victory_bg, (0, 0))
        text = ch_font.render("你贏了！按 ENTER 再玩一次", True, WHITE)
        screen.blit(text, (WIDTH // 2 - 200, HEIGHT - 100))

    # === 失敗畫面 ===
    elif game_state == "defeat":
        screen.blit(defeat_bg, (0, 0))
        text = ch_font.render("你輸了！按 ENTER 再試一次", True, WHITE)
        screen.blit(text, (WIDTH // 2 - 200, HEIGHT - 100))

    # === 處理事件 ===
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key in move_keys:
                move_keys[event.key] = True
            if game_state in ["victory", "defeat"] and event.key == pygame.K_RETURN:
                reset_game()

        elif event.type == pygame.KEYUP:
            if event.key in move_keys:
                move_keys[event.key] = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if game_state == "intro_image" and intro_button_rect.collidepoint(event.pos):
                game_state = "intro"

            elif game_state == "intro" and button_rect.collidepoint(event.pos):
                game_state = "map"

            elif game_state == "map" and battle_prompt:
                enemy = battle_prompt
                map_enemies.remove(enemy)
                battle_prompt = None
                player.damage_history.clear()
                game_state = "battle"

            elif game_state == "battle":
                for skill in skills:
                    if skill["rect"].collidepoint(event.pos):
                        base_damage = skill["damage"]
                        skill_element = skill["element"]
                        skill_name = skill["text"]

                        if skill_name == "監視之眼":
                            player.heal(10)
                            next_turn_buff = True
                            player.damage_history.append("監視之眼: 回復10HP，下一擊強化")
                            enemy.take_damage(0, "監視之眼")
                        else:
                            if next_turn_buff:
                                base_damage = int(base_damage * 1.5)
                                next_turn_buff = False
                            if skill_element == enemy.weakness:
                                damage = int(base_damage * 1.5)
                            else:
                                damage = base_damage
                            enemy.take_damage(damage, skill_name)

                        if enemy.hp <= 0:
                            game_state = "map"
                            player.damage_history.clear()
                            break

                        player.take_damage(enemy.attack, "敵人攻擊")

                        if player.hp <= 0:
                            game_state = "defeat"
                            break

    # === 偵測碰撞敵人觸發戰鬥 ===
    if game_state == "map" and not battle_prompt:
        for m in map_enemies:
            if abs(player.pos[0] - m.pos[0]) < 64 and abs(player.pos[1] - m.pos[1]) < 64:
                battle_prompt = m
                break

    pygame.display.flip()

pygame.quit()


