import pygame, sys, random, math, json, os

# --------------------- 自动存档相关函数 ---------------------
def load_game_record():
    if os.path.exists("savegame.json"):
        with open("savegame.json", "r") as f:
            return json.load(f)
    else:
        return None

def save_game_record(coin_count, purchased_skins, selected_skin, purchased_heads, selected_head, reputation_level, reputation_upgrade_cost):
    data = {
        "coin_count": coin_count,
        "purchased_skins": purchased_skins,
        "selected_skin": selected_skin,
        "purchased_heads": purchased_heads,
        "selected_head": selected_head,
        "reputation_level": reputation_level,
        "reputation_upgrade_cost": reputation_upgrade_cost
    }
    with open("savegame.json", "w") as f:
        json.dump(data, f)

def exit_game(coin_count, purchased_skins, selected_skin, purchased_heads, selected_head):
    save_game_record(coin_count, purchased_skins, selected_skin, purchased_heads, selected_head, reputation_level, reputation_upgrade_cost)
    pygame.quit()
    sys.exit()

# --------------------- 基础设置 ---------------------
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 800
CELL_SIZE = 20
CELL_WIDTH = WINDOW_WIDTH // CELL_SIZE  # e.g. 50
CELL_HEIGHT = WINDOW_HEIGHT // CELL_SIZE  # e.g. 40

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED   = (255, 0, 0)
GRAY  = (128, 128, 128)
GOLD  = (255, 215, 0)  # 用于金币文本

# 下面是 30 种可供购买的皮肤颜色（扩展自原来的 20 种）
SKIN_COLORS = [
    (255, 0, 0),      (0, 255, 0),    (0, 0, 255),      (255, 255, 0),
    (255, 0, 255),    (0, 255, 255),  (128, 128, 128),  (255, 128, 0),
    (128, 0, 128),    (0, 128, 128),  (128, 255, 128),  (255, 128, 128),
    (128, 128, 255),  (255, 255, 128),(255, 128, 255),  (128, 255, 255),
    (192, 192, 192),  (64, 64, 64),   (255, 200, 100),  (100, 200, 255),
    (0, 100, 0),      (75, 0, 130),   (173, 216, 230),  (240, 230, 140),
    (152, 251, 152),  (0, 191, 255),  (219, 112, 147),  (255, 182, 193),
    (160, 32, 240),   (255, 105, 180)
]

# --------------------- 新增：20 个头饰（以颜色表示）及价格 ---------------------
HEAD_ITEMS = [
    (100, 0, 0),    (0, 100, 0),    (0, 0, 100),    (100, 100, 0),
    (100, 0, 100),  (0, 100, 100),  (150, 150, 150),(255, 165, 0),
    (128, 0, 0),    (0, 128, 0),    (0, 0, 128),    (128, 128, 0),
    (128, 0, 128),  (0, 128, 128),  (64, 0, 0),     (0, 64, 0),
    (0, 0, 64),     (64, 64, 0),    (64, 0, 64),    (0, 64, 64)
]
HEAD_COST = 200  # 每个头饰的购买价格

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

# --------------------- 全局变量 ---------------------
muted = False  # 声音初始为开启状态

# 新增：声望等级及其升级价格，全局变量
reputation_level = 0
reputation_upgrade_cost = 50

# --------------------- 覆盖菜单相关全局变量 ---------------------
OVERLAY_RESTART_RECT = pygame.Rect(10, 10, 100, 30)
OVERLAY_QUIT_RECT = pygame.Rect(10, 50, 100, 30)
OVERLAY_VOLUME_RECT = pygame.Rect(10, 90, 100, 30)

# --------------------- 绘制函数 ---------------------
def draw_snake(surface, snake_coords, snake_color, head_item=None):
    """绘制蛇（使用选定的皮肤颜色），在蛇头上加上笑脸标识。
       如果 head_item 不为 None，则在蛇头上绘制头饰（简单用三角形表示）。"""
    for i, coord in enumerate(snake_coords):
        x = coord['x'] * CELL_SIZE
        y = coord['y'] * CELL_SIZE
        rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(surface, snake_color, rect)
        # 如果是蛇头，则绘制笑脸
        if i == 0:
            center_x = x + CELL_SIZE // 2
            center_y = y + CELL_SIZE // 2
            eye_radius = 2
            eye_offset_x = 4
            eye_offset_y = 4
            pygame.draw.circle(surface, BLACK, (center_x - eye_offset_x, center_y - eye_offset_y), eye_radius)
            pygame.draw.circle(surface, BLACK, (center_x + eye_offset_x, center_y - eye_offset_y), eye_radius)
            mouth_rect = pygame.Rect(x + 3, y + CELL_SIZE // 2, CELL_SIZE - 6, CELL_SIZE // 2)
            pygame.draw.arc(surface, BLACK, mouth_rect, math.pi, 2*math.pi, 3)
            # 如果有头饰，则在蛇头上绘制一个三角形帽子
            if head_item is not None:
                hat_points = [
                    (x, y), 
                    (x + CELL_SIZE, y),
                    (x + CELL_SIZE/2, y - CELL_SIZE/2)
                ]
                pygame.draw.polygon(surface, head_item, hat_points)

def draw_apple(surface, apple):
    """绘制苹果（基于像素坐标）。"""
    rect = pygame.Rect(int(apple['x']), int(apple['y']), CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(surface, RED, rect)

def draw_obstacles(surface, obstacles):
    """绘制地图上的所有障碍物。"""
    for obs in obstacles:
        x = obs['x'] * CELL_SIZE
        y = obs['y'] * CELL_SIZE
        rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(surface, GRAY, rect)

def draw_overlay_menu(screen, font_overlay, muted):
    """在屏幕左上角绘制始终可见的覆盖菜单。"""
    pygame.draw.rect(screen, WHITE, OVERLAY_RESTART_RECT, 2)
    pygame.draw.rect(screen, WHITE, OVERLAY_QUIT_RECT, 2)
    pygame.draw.rect(screen, WHITE, OVERLAY_VOLUME_RECT, 2)
    restart_text = font_overlay.render("Restart", True, WHITE)
    quit_text = font_overlay.render("Quit", True, WHITE)
    volume_text = font_overlay.render("Volume: " + ("Off" if muted else "On"), True, WHITE)
    screen.blit(restart_text, (OVERLAY_RESTART_RECT.x + 5, OVERLAY_RESTART_RECT.y + 5))
    screen.blit(quit_text, (OVERLAY_QUIT_RECT.x + 5, OVERLAY_QUIT_RECT.y + 5))
    screen.blit(volume_text, (OVERLAY_VOLUME_RECT.x + 5, OVERLAY_VOLUME_RECT.y + 5))

# --------------------- 障碍物、随机位置 ---------------------
def create_obstacles():
    """
    随机生成 30 个短障碍，每个障碍段长度在 1~2 之间，
    并避免左上角 10x10 的安全区。
    """
    obstacles = set()
    num_segments = 30
    max_length = 2
    safe_zone = {(x, y) for x in range(10) for y in range(10)}
    for _ in range(num_segments):
        while True:
            start_x = random.randint(0, CELL_WIDTH - 1)
            start_y = random.randint(0, CELL_HEIGHT - 1)
            if (start_x, start_y) not in safe_zone:
                break
        orientation = random.choice(['horizontal', 'vertical'])
        length = random.randint(1, max_length)
        for i in range(length):
            if orientation == 'horizontal':
                x = start_x + i
                y = start_y
            else:
                x = start_x
                y = start_y + i
            if 0 <= x < CELL_WIDTH and 0 <= y < CELL_HEIGHT:
                obstacles.add((x, y))
    return [{'x': x, 'y': y} for (x, y) in obstacles]

def get_random_location(obstacles=None):
    """获取随机网格位置，若 obstacles 不为空，则不与障碍物重叠。"""
    while True:
        loc = {'x': random.randint(0, CELL_WIDTH - 1), 'y': random.randint(0, CELL_HEIGHT - 1)}
        if obstacles and any(loc['x'] == obs['x'] and loc['y'] == obs['y'] for obs in obstacles):
            continue
        return loc

# --------------------- 苹果随机移动（Snake模式） ---------------------
def update_apple_position(apple, snake_coords, obstacles):
    """
    在 Snake 模式下，苹果有 50% 的几率随机移动一格。
    """
    if random.random() < 0.5:
        moves = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        random.shuffle(moves)
        for dx, dy in moves:
            new_x = apple['x'] + dx
            new_y = apple['y'] + dy
            if not (0 <= new_x < CELL_WIDTH and 0 <= new_y < CELL_HEIGHT):
                continue
            if any(seg['x'] == new_x and seg['y'] == new_y for seg in snake_coords):
                continue
            if any(obs['x'] == new_x and obs['y'] == new_y for obs in obstacles):
                continue
            apple['x'] = new_x
            apple['y'] = new_y
            break
    return apple

# --------------------- 游戏结束 ---------------------
def game_over(screen, clock, collision_sound, coin_count, purchased_skins, selected_skin, purchased_heads, selected_head):
    """显示 Game Over 并暂停 2 秒，同时播放碰撞音效，然后返回主菜单。"""
    collision_sound.play()
    font_over = pygame.font.SysFont(None, 48)
    text = font_over.render("Game Over", True, RED)
    rect = text.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
    screen.fill(BLACK)
    screen.blit(text, rect)
    pygame.display.update()
    pygame.time.wait(2000)
    return "MENU", coin_count, purchased_skins, selected_skin, purchased_heads, selected_head

# --------------------- Snake模式 ---------------------
def game_loop(screen, clock, apple_eat_sound, collision_sound, coin_count, purchased_skins, selected_skin, purchased_heads, selected_head):
    """
    玩家控制蛇的模式：
      - 吃苹果 +10 金币
      - 蛇头碰到身体或出界则游戏结束
      - 蛇移动若碰到障碍则停留
      - 使用 selected_skin 对应的颜色绘制蛇，同时在蛇头上绘制选购的头饰（若有）
    新增覆盖菜单，允许随时重启、退出（返回主菜单）或切换音量状态
    返回 (state, coin_count, purchased_skins, selected_skin, purchased_heads, selected_head) 以便在主循环更新记录。
    """
    global muted
    while True:  # 外层循环，支持重启
        restart_pressed = False
        snake_coords = [
            {'x': 3, 'y': 5},
            {'x': 2, 'y': 5},
            {'x': 1, 'y': 5}
        ]
        direction = RIGHT
        obstacles = create_obstacles()
        apple = get_random_location(obstacles)
        overlay_font = pygame.font.SysFont(None, 24)

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit_game(coin_count, purchased_skins, selected_skin, purchased_heads, selected_head)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        exit_game(coin_count, purchased_skins, selected_skin, purchased_heads, selected_head)
                    if event.key == pygame.K_UP:
                        direction = UP
                    elif event.key == pygame.K_DOWN:
                        direction = DOWN
                    elif event.key == pygame.K_LEFT:
                        direction = LEFT
                    elif event.key == pygame.K_RIGHT:
                        direction = RIGHT
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if OVERLAY_RESTART_RECT.collidepoint(pos):
                        restart_pressed = True
                        running = False
                        break
                    elif OVERLAY_QUIT_RECT.collidepoint(pos):
                        return "MENU", coin_count, purchased_skins, selected_skin, purchased_heads, selected_head
                    elif OVERLAY_VOLUME_RECT.collidepoint(pos):
                        muted = not muted
                        apple_eat_sound.set_volume(0 if muted else 1)
                        collision_sound.set_volume(0 if muted else 1)
            if not running:
                break

            head = snake_coords[0].copy()
            if direction == UP:
                head['y'] -= 1
            elif direction == DOWN:
                head['y'] += 1
            elif direction == LEFT:
                head['x'] -= 1
            elif direction == RIGHT:
                head['x'] += 1

            if not (0 <= head['x'] < CELL_WIDTH and 0 <= head['y'] < CELL_HEIGHT):
                return game_over(screen, clock, collision_sound, coin_count, purchased_skins, selected_skin, purchased_heads, selected_head)
            if any(obs['x'] == head['x'] and obs['y'] == head['y'] for obs in obstacles):
                head = snake_coords[0].copy()
            else:
                if head in snake_coords[1:]:
                    return game_over(screen, clock, collision_sound, coin_count, purchased_skins, selected_skin, purchased_heads, selected_head)

            if head != snake_coords[0]:
                snake_coords.insert(0, head)
                if head['x'] == apple['x'] and head['y'] == apple['y']:
                    apple_eat_sound.play()
                    coin_count += 10
                    apple = get_random_location(obstacles)
                else:
                    snake_coords.pop()

            apple = update_apple_position(apple, snake_coords, obstacles)

            screen.fill(BLACK)
            draw_obstacles(screen, obstacles)
            snake_color = SKIN_COLORS[selected_skin]
            head_item = HEAD_ITEMS[selected_head] if selected_head != -1 else None
            draw_snake(screen, snake_coords, snake_color, head_item)
            apple_pixel = {'x': apple['x'] * CELL_SIZE, 'y': apple['y'] * CELL_SIZE}
            draw_apple(screen, apple_pixel)
            draw_overlay_menu(screen, overlay_font, muted)
            pygame.display.update()
            clock.tick(16)
        
        if restart_pressed:
            continue

# --------------------- AI 控制蛇的简单函数 ---------------------
def get_snake_direction(snake_coords, apple, obstacles):
    head = snake_coords[0]
    dx = apple['x'] - head['x']
    dy = apple['y'] - head['y']
    candidate_dirs = []
    if abs(dx) >= abs(dy):
        if dx > 0:
            candidate_dirs.append(RIGHT)
        elif dx < 0:
            candidate_dirs.append(LEFT)
        if dy > 0:
            candidate_dirs.append(DOWN)
        elif dy < 0:
            candidate_dirs.append(UP)
    else:
        if dy > 0:
            candidate_dirs.append(DOWN)
        elif dy < 0:
            candidate_dirs.append(UP)
        if dx > 0:
            candidate_dirs.append(RIGHT)
        elif dx < 0:
            candidate_dirs.append(LEFT)
    for d in [UP, DOWN, LEFT, RIGHT]:
        if d not in candidate_dirs:
            candidate_dirs.append(d)

    for d in candidate_dirs:
        new_head = head.copy()
        if d == UP:
            new_head['y'] -= 1
        elif d == DOWN:
            new_head['y'] += 1
        elif d == LEFT:
            new_head['x'] -= 1
        elif d == RIGHT:
            new_head['x'] += 1
        if not (0 <= new_head['x'] < CELL_WIDTH and 0 <= new_head['y'] < CELL_HEIGHT):
            continue
        if new_head in snake_coords[1:]:
            continue
        if any(obs['x'] == new_head['x'] and obs['y'] == new_head['y'] for obs in obstacles):
            continue
        return d
    return None

# --------------------- Apple模式 ---------------------
def game_loop_apple(screen, clock, apple_eat_sound, collision_sound, coin_count, purchased_skins, selected_skin, purchased_heads, selected_head):
    global muted
    while True:
        restart_pressed = False
        snake_coords = [
            {'x': 3, 'y': 5},
            {'x': 2, 'y': 5},
            {'x': 1, 'y': 5}
        ]
        obstacles = create_obstacles()
        apple = get_random_location(obstacles)
        apple_direction = RIGHT
        overlay_font = pygame.font.SysFont(None, 24)

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit_game(coin_count, purchased_skins, selected_skin, purchased_heads, selected_head)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        exit_game(coin_count, purchased_skins, selected_skin, purchased_heads, selected_head)
                    if event.key == pygame.K_UP:
                        apple_direction = UP
                    elif event.key == pygame.K_DOWN:
                        apple_direction = DOWN
                    elif event.key == pygame.K_LEFT:
                        apple_direction = LEFT
                    elif event.key == pygame.K_RIGHT:
                        apple_direction = RIGHT
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if OVERLAY_RESTART_RECT.collidepoint(pos):
                        restart_pressed = True
                        running = False
                        break
                    elif OVERLAY_QUIT_RECT.collidepoint(pos):
                        return "MENU", coin_count, purchased_skins, selected_skin, purchased_heads, selected_head
                    elif OVERLAY_VOLUME_RECT.collidepoint(pos):
                        muted = not muted
                        apple_eat_sound.set_volume(0 if muted else 1)
                        collision_sound.set_volume(0 if muted else 1)
            if not running:
                break

            new_apple = apple.copy()
            if apple_direction == UP:
                new_apple['y'] -= 1
            elif apple_direction == DOWN:
                new_apple['y'] += 1
            elif apple_direction == LEFT:
                new_apple['x'] -= 1
            elif apple_direction == RIGHT:
                new_apple['x'] += 1
            if (0 <= new_apple['x'] < CELL_WIDTH and 0 <= new_apple['y'] < CELL_HEIGHT) and \
               not any(obs['x'] == new_apple['x'] and obs['y'] == new_apple['y'] for obs in obstacles):
                apple = new_apple

            snake_direction = get_snake_direction(snake_coords, apple, obstacles)
            if snake_direction:
                head = snake_coords[0].copy()
                if snake_direction == UP:
                    head['y'] -= 1
                elif snake_direction == DOWN:
                    head['y'] += 1
                elif snake_direction == LEFT:
                    head['x'] -= 1
                elif snake_direction == RIGHT:
                    head['x'] += 1
                if not (0 <= head['x'] < CELL_WIDTH and 0 <= head['y'] < CELL_HEIGHT):
                    new_head = snake_coords[0].copy()
                else:
                    new_head = head
                    if new_head in snake_coords[1:]:
                        return game_over(screen, clock, collision_sound, coin_count, purchased_skins, selected_skin, purchased_heads, selected_head)
            else:
                new_head = snake_coords[0].copy()

            if new_head != snake_coords[0]:
                snake_coords.insert(0, new_head)
                if new_head['x'] == apple['x'] and new_head['y'] == apple['y']:
                    apple_eat_sound.play()
                    coin_count += 10
                    apple = get_random_location(obstacles)
                else:
                    snake_coords.pop()

            screen.fill(BLACK)
            draw_obstacles(screen, obstacles)
            snake_color = SKIN_COLORS[selected_skin]
            head_item = HEAD_ITEMS[selected_head] if selected_head != -1 else None
            draw_snake(screen, snake_coords, snake_color, head_item)
            apple_pixel = {'x': apple['x'] * CELL_SIZE, 'y': apple['y'] * CELL_SIZE}
            draw_apple(screen, apple_pixel)
            draw_overlay_menu(screen, overlay_font, muted)
            pygame.display.update()
            clock.tick(16)
        
        if restart_pressed:
            continue

# --------------------- 2 Players 模式 ---------------------
def game_loop_2players(screen, clock, apple_eat_sound, collision_sound, snake_eaten_sound,
                        coin_count, purchased_skins, selected_skin, purchased_heads, selected_head):
    global muted
    while True:
        restart_pressed = False
        snake1_coords = [{'x': 5, 'y': 10}, {'x': 4, 'y': 10}, {'x': 3, 'y': 10}]
        snake2_coords = [{'x': CELL_WIDTH - 6, 'y': 10}, {'x': CELL_WIDTH - 5, 'y': 10}, {'x': CELL_WIDTH - 4, 'y': 10}]
        direction1 = RIGHT
        direction2 = LEFT
        apple = get_random_location()
        apple_count = 0
        phase = 1
        overlay_font = pygame.font.SysFont(None, 24)

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit_game(coin_count, purchased_skins, selected_skin, purchased_heads, selected_head)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        exit_game(coin_count, purchased_skins, selected_skin, purchased_heads, selected_head)
                    if event.key == pygame.K_UP:
                        direction1 = UP
                    elif event.key == pygame.K_DOWN:
                        direction1 = DOWN
                    elif event.key == pygame.K_LEFT:
                        direction1 = LEFT
                    elif event.key == pygame.K_RIGHT:
                        direction1 = RIGHT
                    if event.key == pygame.K_w:
                        direction2 = UP
                    elif event.key == pygame.K_s:
                        direction2 = DOWN
                    elif event.key == pygame.K_a:
                        direction2 = LEFT
                    elif event.key == pygame.K_d:
                        direction2 = RIGHT
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if OVERLAY_RESTART_RECT.collidepoint(pos):
                        restart_pressed = True
                        running = False
                        break
                    elif OVERLAY_QUIT_RECT.collidepoint(pos):
                        return "MENU", coin_count, purchased_skins, selected_skin, purchased_heads, selected_head
                    elif OVERLAY_VOLUME_RECT.collidepoint(pos):
                        muted = not muted
                        apple_eat_sound.set_volume(0 if muted else 1)
                        collision_sound.set_volume(0 if muted else 1)
                        snake_eaten_sound.set_volume(0 if muted else 1)
            if not running:
                break

            new_head1 = snake1_coords[0].copy()
            if direction1 == UP:
                new_head1['y'] -= 1
            elif direction1 == DOWN:
                new_head1['y'] += 1
            elif direction1 == LEFT:
                new_head1['x'] -= 1
            elif direction1 == RIGHT:
                new_head1['x'] += 1

            new_head2 = snake2_coords[0].copy()
            if direction2 == UP:
                new_head2['y'] -= 1
            elif direction2 == DOWN:
                new_head2['y'] += 1
            elif direction2 == LEFT:
                new_head2['x'] -= 1
            elif direction2 == RIGHT:
                new_head2['x'] += 1

            if not (0 <= new_head1['x'] < CELL_WIDTH and 0 <= new_head1['y'] < CELL_HEIGHT):
                return game_over(screen, clock, collision_sound, coin_count, purchased_skins, selected_skin, purchased_heads, selected_head)
            if not (0 <= new_head2['x'] < CELL_WIDTH and 0 <= new_head2['y'] < CELL_HEIGHT):
                return game_over(screen, clock, collision_sound, coin_count, purchased_skins, selected_skin, purchased_heads, selected_head)

            if phase == 1:
                snake1_grow = False
                snake2_grow = False
                if new_head1['x'] == apple['x'] and new_head1['y'] == apple['y']:
                    snake1_grow = True
                    apple_eat_sound.play()
                    apple_count += 1
                    apple = get_random_location()
                if new_head2['x'] == apple['x'] and new_head2['y'] == apple['y']:
                    snake2_grow = True
                    apple_eat_sound.play()
                    apple_count += 1
                    apple = get_random_location()

                snake1_coords.insert(0, new_head1)
                snake2_coords.insert(0, new_head2)
                if not snake1_grow:
                    snake1_coords.pop()
                if not snake2_grow:
                    snake2_coords.pop()

                if apple_count >= 5:
                    phase = 2
            else:
                snake1_coords.insert(0, new_head1)
                snake2_coords.insert(0, new_head2)
                collision1 = False
                collision2 = False
                for seg in snake2_coords[1:]:
                    if new_head1['x'] == seg['x'] and new_head1['y'] == seg['y']:
                        collision1 = True
                        break
                for seg in snake1_coords[1:]:
                    if new_head2['x'] == seg['x'] and new_head2['y'] == seg['y']:
                        collision2 = True
                        break

                if collision1:
                    if len(snake2_coords) > 1:
                        snake2_coords.pop()
                        snake_eaten_sound.play()
                else:
                    snake1_coords.pop()

                if collision2:
                    if len(snake1_coords) > 1:
                        snake1_coords.pop()
                        snake_eaten_sound.play()
                else:
                    snake2_coords.pop()

                if len(snake1_coords) <= 1 or len(snake2_coords) <= 1:
                    return game_over(screen, clock, collision_sound, coin_count, purchased_skins, selected_skin, purchased_heads, selected_head)

            screen.fill(BLACK)
            if phase == 1:
                apple_pixel = {'x': apple['x'] * CELL_SIZE, 'y': apple['y'] * CELL_SIZE}
                draw_apple(screen, apple_pixel)
            snake1_color = SKIN_COLORS[selected_skin]
            head_item = HEAD_ITEMS[selected_head] if selected_head != -1 else None
            snake2_color = SKIN_COLORS[0]
            draw_snake(screen, snake1_coords, snake1_color, head_item)
            draw_snake(screen, snake2_coords, snake2_color)
            draw_overlay_menu(screen, overlay_font, muted)
            info_font = pygame.font.SysFont(None, 24)
            if phase == 1:
                info_text = info_font.render(f"Phase 1: {apple_count} apple(s) eaten", True, WHITE)
            else:
                info_text = info_font.render("Phase 2: Mutual Eating", True, WHITE)
            screen.blit(info_text, (WINDOW_WIDTH//2 - 100, 20))
            pygame.display.update()
            clock.tick(16)
        if restart_pressed:
            continue

# --------------------- 皮肤商店（包含皮肤和头饰切换） ---------------------
def skins_loop(screen, clock, font_button, coin_count, purchased_skins, selected_skin, purchased_heads, selected_head):
    shop_mode = "skins"
    confirm_purchase_item = None
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit_game(coin_count, purchased_skins, selected_skin, purchased_heads, selected_head)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "MENU", coin_count, purchased_skins, selected_skin, purchased_heads, selected_head
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                switch_rect = pygame.Rect(50, 100, 150, 40)
                if switch_rect.collidepoint(mx, my):
                    shop_mode = "head" if shop_mode == "skins" else "skins"
                    continue
                if confirm_purchase_item is not None:
                    CONFIRM_WIDTH = 400
                    CONFIRM_HEIGHT = 200
                    confirm_rect = pygame.Rect((WINDOW_WIDTH - CONFIRM_WIDTH) // 2, (WINDOW_HEIGHT - CONFIRM_HEIGHT) // 2, CONFIRM_WIDTH, CONFIRM_HEIGHT)
                    yes_rect = pygame.Rect(confirm_rect.x + 50, confirm_rect.y + CONFIRM_HEIGHT - 60, 100, 40)
                    no_rect = pygame.Rect(confirm_rect.x + CONFIRM_WIDTH - 150, confirm_rect.y + CONFIRM_HEIGHT - 60, 100, 40)
                    if yes_rect.collidepoint(mx, my):
                        price = 100 if shop_mode == "skins" else HEAD_COST
                        if coin_count >= price:
                            coin_count -= price
                            if shop_mode == "skins":
                                purchased_skins[confirm_purchase_item] = True
                                selected_skin = confirm_purchase_item
                            else:
                                purchased_heads[confirm_purchase_item] = True
                                selected_head = confirm_purchase_item
                        confirm_purchase_item = None
                    elif no_rect.collidepoint(mx, my):
                        confirm_purchase_item = None
                else:
                    preview_area = pygame.Rect(600, 150, 300, 300)
                    price = 100 if shop_mode == "skins" else HEAD_COST
                    if shop_mode == "skins":
                        if not purchased_skins[selected_skin] and coin_count >= price:
                            purchase_button_rect = pygame.Rect(preview_area.x + (preview_area.width - 120)//2, preview_area.y + preview_area.height + 20, 120, 40)
                            if purchase_button_rect.collidepoint(mx, my):
                                confirm_purchase_item = selected_skin
                                continue
                    else:
                        if not purchased_heads[selected_head] and coin_count >= price:
                            purchase_button_rect = pygame.Rect(preview_area.x + (preview_area.width - 120)//2, preview_area.y + preview_area.height + 20, 120, 40)
                            if purchase_button_rect.collidepoint(mx, my):
                                confirm_purchase_item = selected_head
                                continue
                    padding = 20
                    box_size = 40
                    start_x = 50
                    start_y = 150
                    items = SKIN_COLORS if shop_mode == "skins" else HEAD_ITEMS
                    for i, item in enumerate(items):
                        row = i // 4
                        col = i % 4
                        bx = start_x + col * (box_size + padding)
                        by = start_y + row * (box_size + padding)
                        rect = pygame.Rect(bx, by, box_size, box_size)
                        if rect.collidepoint(mx, my):
                            if shop_mode == "skins":
                                selected_skin = i
                            else:
                                selected_head = i
                            break
                    back_text = font_button.render("Back to Menu", True, WHITE)
                    back_rect = back_text.get_rect(topleft=(50, 650))
                    if back_rect.inflate(20, 10).collidepoint(mx, my):
                        return "MENU", coin_count, purchased_skins, selected_skin, purchased_heads, selected_head

        screen.fill(BLACK)
        switch_text = "Switch to Headwear" if shop_mode == "skins" else "Switch to Skins"
        switch_button = font_button.render(switch_text, True, WHITE)
        switch_rect = switch_button.get_rect(topleft=(50, 100))
        pygame.draw.rect(screen, WHITE, switch_rect.inflate(20, 10), 2)
        screen.blit(switch_button, switch_rect)

        title_font = pygame.font.SysFont(None, 48)
        title_text = title_font.render("Shop", True, WHITE)
        screen.blit(title_text, (50, 50))
        price = 100 if shop_mode == "skins" else HEAD_COST
        coin_text = font_button.render(f"Coins: {coin_count}", True, GOLD)
        screen.blit(coin_text, (WINDOW_WIDTH - 200, 50))
        padding = 20
        box_size = 40
        start_x = 50
        start_y = 150
        label_font = pygame.font.SysFont(None, 24)
        items = SKIN_COLORS if shop_mode == "skins" else HEAD_ITEMS
        purchased = purchased_skins if shop_mode == "skins" else purchased_heads
        selected = selected_skin if shop_mode == "skins" else selected_head
        for i, item in enumerate(items):
            row = i // 4
            col = i % 4
            bx = start_x + col * (box_size + padding)
            by = start_y + row * (box_size + padding)
            rect = pygame.Rect(bx, by, box_size, box_size)
            pygame.draw.rect(screen, item, rect)
            if purchased[i]:
                label = label_font.render("Owned", True, WHITE)
            else:
                label = label_font.render(f"{price} coins", True, WHITE)
            label_rect = label.get_rect(center=(bx + box_size/2, by + box_size + 12))
            screen.blit(label, label_rect)
            if i == selected:
                pygame.draw.rect(screen, WHITE, rect, 3)

        preview_area = pygame.Rect(600, 150, 300, 300)
        pygame.draw.rect(screen, GRAY, preview_area, 2)
        preview_title = label_font.render("Preview", True, WHITE)
        preview_title_rect = preview_title.get_rect(center=(preview_area.centerx, preview_area.y - 20))
        screen.blit(preview_title, preview_title_rect)
        if shop_mode == "skins":
            preview_segment_size = 40
            spacing = 10
            total_width = 3 * preview_segment_size + 2 * spacing
            start_preview_x = preview_area.x + (preview_area.width - total_width) // 2
            start_preview_y = preview_area.y + (preview_area.height - preview_segment_size) // 2
            for i in range(3):
                seg_rect = pygame.Rect(start_preview_x + i*(preview_segment_size + spacing), start_preview_y, preview_segment_size, preview_segment_size)
                pygame.draw.rect(screen, items[selected], seg_rect)
                pygame.draw.rect(screen, WHITE, seg_rect, 2)
        else:
            hat_points = [
                (preview_area.centerx - 50, preview_area.centery),
                (preview_area.centerx + 50, preview_area.centery),
                (preview_area.centerx, preview_area.centery - 50)
            ]
            pygame.draw.polygon(screen, items[selected], hat_points)
            pygame.draw.polygon(screen, WHITE, hat_points, 2)
        if not purchased[selected] and coin_count >= price:
            purchase_button_rect = pygame.Rect(preview_area.x + (preview_area.width - 120)//2, preview_area.y + preview_area.height + 20, 120, 40)
            pygame.draw.rect(screen, WHITE, purchase_button_rect, 2)
            purchase_text = label_font.render("Purchase", True, WHITE)
            purchase_text_rect = purchase_text.get_rect(center=purchase_button_rect.center)
            screen.blit(purchase_text, purchase_text_rect)
        elif not purchased[selected]:
            insufficient_text = label_font.render("Not enough coins", True, RED)
            insufficient_text_rect = insufficient_text.get_rect(center=(preview_area.centerx, preview_area.y + preview_area.height + 20))
            screen.blit(insufficient_text, insufficient_text_rect)

        back_text = font_button.render("Back to Menu", True, WHITE)
        back_rect = back_text.get_rect(topleft=(50, 650))
        pygame.draw.rect(screen, WHITE, back_rect.inflate(20,10), 2)
        screen.blit(back_text, back_rect)

        if confirm_purchase_item is not None:
            CONFIRM_WIDTH = 400
            CONFIRM_HEIGHT = 200
            confirm_rect = pygame.Rect((WINDOW_WIDTH - CONFIRM_WIDTH) // 2, (WINDOW_HEIGHT - CONFIRM_HEIGHT) // 2, CONFIRM_WIDTH, CONFIRM_HEIGHT)
            pygame.draw.rect(screen, GRAY, confirm_rect)
            pygame.draw.rect(screen, WHITE, confirm_rect, 2)
            confirm_font = pygame.font.SysFont(None, 36)
            confirm_text = confirm_font.render(f"Purchase for {price} coins?", True, WHITE)
            text_rect = confirm_text.get_rect(center=(confirm_rect.centerx, confirm_rect.y + 50))
            screen.blit(confirm_text, text_rect)
            yes_rect = pygame.Rect(confirm_rect.x + 50, confirm_rect.y + CONFIRM_HEIGHT - 60, 100, 40)
            no_rect = pygame.Rect(confirm_rect.x + CONFIRM_WIDTH - 150, confirm_rect.y + CONFIRM_HEIGHT - 60, 100, 40)
            pygame.draw.rect(screen, WHITE, yes_rect, 2)
            pygame.draw.rect(screen, WHITE, no_rect, 2)
            button_font = pygame.font.SysFont(None, 28)
            yes_text = button_font.render("Yes", True, WHITE)
            no_text = button_font.render("No", True, WHITE)
            yes_text_rect = yes_text.get_rect(center=yes_rect.center)
            no_text_rect = no_text.get_rect(center=no_rect.center)
            screen.blit(yes_text, yes_text_rect)
            screen.blit(no_text, no_text_rect)

        pygame.display.update()
        clock.tick(15)

# --------------------- 新增：根据声望等级绘制主菜单背景 ---------------------
def draw_menu_background(screen, reputation_level):
    if reputation_level == 0:
        screen.fill(BLACK)
        for _ in range(120):
            x = random.randint(0, WINDOW_WIDTH)
            y = random.randint(0, WINDOW_HEIGHT)
            pygame.draw.circle(screen, (20, 20, 20), (x, y), random.randint(1, 2))
    elif reputation_level == 1:
        screen.fill((0, 0, 50))
        for _ in range(120):
            x = random.randint(0, WINDOW_WIDTH)
            y = random.randint(0, WINDOW_HEIGHT)
            pygame.draw.circle(screen, (220, 220, 220), (x, y), random.randint(1, 3))
    elif reputation_level == 2:
        screen.fill((30, 30, 60))
        for _ in range(250):
            x = random.randint(0, WINDOW_WIDTH)
            y = random.randint(0, WINDOW_HEIGHT)
            color = random.choice([(200,200,220), (180,180,200), (160,160,180)])
            pygame.draw.circle(screen, color, (x, y), random.randint(1, 3))
        pygame.draw.circle(screen, (210, 210, 190), (WINDOW_WIDTH - 150, 150), 50)
    elif reputation_level == 3:
        screen.fill((20, 0, 40))
        for _ in range(300):
            x = random.randint(0, WINDOW_WIDTH)
            y = random.randint(0, WINDOW_HEIGHT)
            pygame.draw.line(screen, (90, 90, 110), (x, y), (x + random.randint(-10,10), y + random.randint(-10,10)), 1)
        for _ in range(150):
            x = random.randint(0, WINDOW_WIDTH)
            y = random.randint(0, WINDOW_HEIGHT)
            pygame.draw.circle(screen, (100, 70, 130), (x, y), random.randint(5, 10))
    elif reputation_level == 4:
        screen.fill((10, 10, 10))
        for _ in range(200):
            rect_width = random.randint(10, 50)
            rect_height = random.randint(10, 50)
            x = random.randint(0, WINDOW_WIDTH - rect_width)
            y = random.randint(0, WINDOW_HEIGHT - rect_height)
            color = (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200))
            pygame.draw.rect(screen, color, (x, y, rect_width, rect_height))
        for _ in range(150):
            x = random.randint(0, WINDOW_WIDTH)
            y = random.randint(0, WINDOW_HEIGHT)
            pygame.draw.circle(screen, (220, 220, 220), (x, y), random.randint(5, 15), 2)
    else:
        screen.fill((0, 50, 0))
        num_elements = 250 + reputation_level * 30
        for _ in range(num_elements):
            x = random.randint(0, WINDOW_WIDTH)
            y = random.randint(0, WINDOW_HEIGHT)
            pygame.draw.circle(screen, (240, 240, 220), (x, y), random.randint(1, 3))
        for _ in range(60):
            points = [(random.randint(0, WINDOW_WIDTH), random.randint(0, WINDOW_HEIGHT)) for _ in range(5)]
            pygame.draw.polygon(screen, (random.randint(0,180), random.randint(0,180), random.randint(0,180)), points, 2)

# --------------------- 菜单 ---------------------
def menu_loop(screen, clock, font_title, font_button, game_start_sound,
              coin_count, purchased_skins, selected_skin, purchased_heads, selected_head):
    global reputation_level, reputation_upgrade_cost
    while True:
        draw_menu_background(screen, reputation_level)
        snake_text = font_button.render("Play as Snake", True, WHITE)
        apple_text = font_button.render("Play as Apple", True, WHITE)
        two_players_text = font_button.render("2 Players Mode", True, WHITE)
        shop_text  = font_button.render("Shop", True, WHITE)
        quit_text  = font_button.render("Quit Game", True, WHITE)
        coin_text  = font_button.render(f"Coins: {coin_count}", True, GOLD)
        upgrade_text = font_button.render(f"Upgrade Background ({reputation_upgrade_cost} coins)", True, WHITE)

        snake_rect = snake_text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2 - 100))
        apple_rect = apple_text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2 - 40))
        two_players_rect = two_players_text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2 + 20))
        shop_rect  = shop_text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2 + 80))
        quit_rect  = quit_text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2 + 140))
        upgrade_rect = upgrade_text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2 + 200))
        
        title_text = font_title.render("Snake Game", True, WHITE)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/3))
        coin_rect = coin_text.get_rect(topright=(WINDOW_WIDTH - 20, 20))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit_game(coin_count, purchased_skins, selected_skin, purchased_heads, selected_head)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    exit_game(coin_count, purchased_skins, selected_skin, purchased_heads, selected_head)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if snake_rect.collidepoint(mx, my):
                    game_start_sound.play()
                    return "SNAKE", coin_count, purchased_skins, selected_skin, purchased_heads, selected_head
                elif apple_rect.collidepoint(mx, my):
                    game_start_sound.play()
                    return "APPLE", coin_count, purchased_skins, selected_skin, purchased_heads, selected_head
                elif two_players_rect.collidepoint(mx, my):
                    game_start_sound.play()
                    return "2PLAYERS", coin_count, purchased_skins, selected_skin, purchased_heads, selected_head
                elif shop_rect.collidepoint(mx, my):
                    game_start_sound.play()
                    return "SKINS", coin_count, purchased_skins, selected_skin, purchased_heads, selected_head
                elif quit_rect.collidepoint(mx, my):
                    exit_game(coin_count, purchased_skins, selected_skin, purchased_heads, selected_head)
                elif upgrade_rect.collidepoint(mx, my):
                    if coin_count >= reputation_upgrade_cost:
                        coin_count -= reputation_upgrade_cost
                        reputation_level += 1
                        reputation_upgrade_cost += 50

        screen.blit(title_text, title_rect)
        for text, rect in [(snake_text, snake_rect),
                           (apple_text, apple_rect),
                           (two_players_text, two_players_rect),
                           (shop_text,  shop_rect),
                           (quit_text,  quit_rect),
                           (upgrade_text, upgrade_rect)]:
            pygame.draw.rect(screen, WHITE, rect.inflate(20, 10), 2)
            screen.blit(text, rect)
        screen.blit(coin_text, coin_rect)
        pygame.display.update()
        clock.tick(15)

# --------------------- 主函数 ---------------------
def main():
    pygame.init()
    pygame.mixer.init()

    game_start_sound = pygame.mixer.Sound("game_start.wav")
    apple_eat_sound  = pygame.mixer.Sound("eat_apple.wav")
    collision_sound  = pygame.mixer.Sound("game_over.wav")
    snake_eaten_sound = pygame.mixer.Sound("snake_eaten.wav")

    game_start_sound.set_volume(0 if muted else 1)
    apple_eat_sound.set_volume(0 if muted else 1)
    collision_sound.set_volume(0 if muted else 1)
    snake_eaten_sound.set_volume(0 if muted else 1)

    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Ian's Snake Game")

    font_title  = pygame.font.SysFont(None, 48)
    font_button = pygame.font.SysFont(None, 36)

    # 尝试加载存档记录
    record = load_game_record()
    if record:
        coin_count = record.get("coin_count", 1000)
        purchased_skins = record.get("purchased_skins", [False] * len(SKIN_COLORS))
        selected_skin = record.get("selected_skin", 1)
        purchased_heads = record.get("purchased_heads", [False] * len(HEAD_ITEMS))
        selected_head = record.get("selected_head", -1)
        global reputation_level, reputation_upgrade_cost
        reputation_level = record.get("reputation_level", 0)
        reputation_upgrade_cost = record.get("reputation_upgrade_cost", 50)
    else:
        coin_count = 1000
        purchased_skins = [False] * len(SKIN_COLORS)
        purchased_skins[1] = True
        selected_skin = 1
        purchased_heads = [False] * len(HEAD_ITEMS)
        selected_head = -1

    state = "MENU"
    while True:
        if state == "MENU":
            state, coin_count, purchased_skins, selected_skin, purchased_heads, selected_head = menu_loop(
                screen, clock, font_title, font_button, game_start_sound,
                coin_count, purchased_skins, selected_skin, purchased_heads, selected_head
            )
        elif state == "SKINS":
            state, coin_count, purchased_skins, selected_skin, purchased_heads, selected_head = skins_loop(
                screen, clock, font_button, coin_count, purchased_skins, selected_skin, purchased_heads, selected_head
            )
        elif state == "SNAKE":
            state, coin_count, purchased_skins, selected_skin, purchased_heads, selected_head = game_loop(
                screen, clock, apple_eat_sound, collision_sound,
                coin_count, purchased_skins, selected_skin, purchased_heads, selected_head
            )
        elif state == "APPLE":
            state, coin_count, purchased_skins, selected_skin, purchased_heads, selected_head = game_loop_apple(
                screen, clock, apple_eat_sound, collision_sound,
                coin_count, purchased_skins, selected_skin, purchased_heads, selected_head
            )
        elif state == "2PLAYERS":
            state, coin_count, purchased_skins, selected_skin, purchased_heads, selected_head = game_loop_2players(
                screen, clock, apple_eat_sound, collision_sound, snake_eaten_sound,
                coin_count, purchased_skins, selected_skin, purchased_heads, selected_head
            )

if __name__ == "__main__":
    main()
