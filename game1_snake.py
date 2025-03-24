import pygame, sys, random, math

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

# 下面是 20 种可供购买的皮肤颜色
SKIN_COLORS = [
    (255,   0,   0),  (  0, 255,   0),  (  0,   0, 255),  (255, 255,   0),
    (255,   0, 255),  (  0, 255, 255),  (128, 128, 128),  (255, 128,   0),
    (128,   0, 128),  (  0, 128, 128),  (128, 255, 128),  (255, 128, 128),
    (128, 128, 255),  (255, 255, 128),  (255, 128, 255),  (128, 255, 255),
    (192, 192, 192),  ( 64,  64,  64),  (255, 200, 100),  (100, 200, 255)
]

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

# --------------------- 覆盖菜单相关全局变量 ---------------------
muted = False  # 声音初始为开启状态
OVERLAY_RESTART_RECT = pygame.Rect(10, 10, 100, 30)
OVERLAY_QUIT_RECT = pygame.Rect(10, 50, 100, 30)
OVERLAY_VOLUME_RECT = pygame.Rect(10, 90, 100, 30)

# --------------------- 绘制函数 ---------------------
def draw_snake(surface, snake_coords, snake_color):
    """绘制蛇（使用选定的皮肤颜色），在蛇头上加上笑脸标识（线宽加粗）。"""
    for i, coord in enumerate(snake_coords):
        x = coord['x'] * CELL_SIZE
        y = coord['y'] * CELL_SIZE
        rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(surface, snake_color, rect)
        # 如果是蛇头，则绘制笑脸
        if i == 0:
            center_x = x + CELL_SIZE // 2
            center_y = y + CELL_SIZE // 2
            # 眼睛参数
            eye_radius = 2
            eye_offset_x = 4
            eye_offset_y = 4
            pygame.draw.circle(surface, BLACK, (center_x - eye_offset_x, center_y - eye_offset_y), eye_radius)
            pygame.draw.circle(surface, BLACK, (center_x + eye_offset_x, center_y - eye_offset_y), eye_radius)
            # 绘制微笑：使用弧线绘制蛇头下半部分，线宽由 1 加粗到 3
            mouth_rect = pygame.Rect(x + 3, y + CELL_SIZE // 2, CELL_SIZE - 6, CELL_SIZE // 2)
            pygame.draw.arc(surface, BLACK, mouth_rect, math.pi, 2*math.pi, 3)

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
def game_over(screen, clock, collision_sound):
    """显示 Game Over 并暂停 2 秒。"""
    collision_sound.play()
    font_over = pygame.font.SysFont(None, 48)
    text = font_over.render("Game Over", True, RED)
    rect = text.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
    screen.fill(BLACK)
    screen.blit(text, rect)
    pygame.display.update()
    pygame.time.wait(2000)

# --------------------- Snake模式 ---------------------
def game_loop(screen, clock, apple_eat_sound, collision_sound, coin_count,
              purchased_skins, selected_skin):
    """
    玩家控制蛇的模式：
      - 吃苹果 +10 金币
      - 蛇头碰到身体或出界则游戏结束
      - 蛇移动若碰到障碍则停留
      - 使用 selected_skin 对应的颜色绘制蛇，并在蛇头上加粗笑脸
    新增覆盖菜单，允许随时重启、退出（返回主菜单）或切换音量状态
    返回 (state, coin_count) 以便在主循环更新金币、回到菜单等。
    """
    global muted
    while True:  # 外层循环，支持重启
        restart_pressed = False
        # 初始化游戏状态
        snake_coords = [
            {'x': 3, 'y': 5},
            {'x': 2, 'y': 5},
            {'x': 1, 'y': 5}
        ]
        direction = RIGHT
        obstacles = create_obstacles()
        apple = get_random_location(obstacles)  # 网格坐标
        overlay_font = pygame.font.SysFont(None, 24)

        running = True
        while running:
            # 处理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                elif event.type == pygame.KEYDOWN:
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
                        running = False
                        return "MENU", coin_count
                    elif OVERLAY_VOLUME_RECT.collidepoint(pos):
                        muted = not muted
                        apple_eat_sound.set_volume(0 if muted else 1)
                        collision_sound.set_volume(0 if muted else 1)
            if not running:
                break

            # 计算新头位置
            head = snake_coords[0].copy()
            if direction == UP:
                head['y'] -= 1
            elif direction == DOWN:
                head['y'] += 1
            elif direction == LEFT:
                head['x'] -= 1
            elif direction == RIGHT:
                head['x'] += 1

            # 出界检查
            if not (0 <= head['x'] < CELL_WIDTH and 0 <= head['y'] < CELL_HEIGHT):
                game_over(screen, clock, collision_sound)
                return "MENU", coin_count

            # 障碍物检查
            if any(obs['x'] == head['x'] and obs['y'] == head['y'] for obs in obstacles):
                # 若下一个位置是障碍，则保持原位不动
                head = snake_coords[0].copy()
            else:
                # 自身碰撞检查
                if head in snake_coords[1:]:
                    game_over(screen, clock, collision_sound)
                    return "MENU", coin_count

            # 如果确实移动了，则插入新头
            if head != snake_coords[0]:
                snake_coords.insert(0, head)
                # 吃苹果
                if head['x'] == apple['x'] and head['y'] == apple['y']:
                    apple_eat_sound.play()
                    coin_count += 10
                    apple = get_random_location(obstacles)
                else:
                    snake_coords.pop()

            # 苹果随机移动
            apple = update_apple_position(apple, snake_coords, obstacles)

            # 绘制游戏画面
            screen.fill(BLACK)
            draw_obstacles(screen, obstacles)
            snake_color = SKIN_COLORS[selected_skin]
            draw_snake(screen, snake_coords, snake_color)
            apple_pixel = {'x': apple['x'] * CELL_SIZE, 'y': apple['y'] * CELL_SIZE}
            draw_apple(screen, apple_pixel)
            draw_overlay_menu(screen, overlay_font, muted)
            pygame.display.update()
            clock.tick(16)
        
        if restart_pressed:
            continue  # 重新开始游戏回合

# --------------------- AI 控制蛇的简单函数 ---------------------
def get_snake_direction(snake_coords, apple, obstacles):
    """
    AI 算法：让蛇尽量向苹果靠近，避免自身和障碍物。
    若没有安全方向，则返回 None（本帧不移动）。
    """
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
    # 补充剩余方向
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
        # 出界
        if not (0 <= new_head['x'] < CELL_WIDTH and 0 <= new_head['y'] < CELL_HEIGHT):
            continue
        # 自身碰撞
        if new_head in snake_coords[1:]:
            continue
        # 障碍物
        if any(obs['x'] == new_head['x'] and obs['y'] == new_head['y'] for obs in obstacles):
            continue
        return d
    return None

# --------------------- Apple模式 ---------------------
def game_loop_apple(screen, clock, apple_eat_sound, collision_sound, coin_count,
                    purchased_skins, selected_skin):
    """
    Apple模式：玩家控制苹果移动，AI 控制蛇追赶苹果。
      - 蛇吃到苹果 +10 金币
      - 蛇头若碰到自身，游戏结束
      - 蛇和苹果的绘制都用 selected_skin 对应的颜色来画“蛇”，并在蛇头上加粗笑脸
    同时增加覆盖菜单，支持重启、退出（返回主菜单）和音量控制
    返回 (state, coin_count)。
    """
    global muted
    while True:  # 外层循环，用于支持重启
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
                    pygame.quit(); sys.exit()
                elif event.type == pygame.KEYDOWN:
                    # 玩家改变苹果方向
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
                        running = False
                        return "MENU", coin_count
                    elif OVERLAY_VOLUME_RECT.collidepoint(pos):
                        muted = not muted
                        apple_eat_sound.set_volume(0 if muted else 1)
                        collision_sound.set_volume(0 if muted else 1)
            
            if not running:
                break

            # 苹果连续移动
            new_apple = apple.copy()
            if apple_direction == UP:
                new_apple['y'] -= 1
            elif apple_direction == DOWN:
                new_apple['y'] += 1
            elif apple_direction == LEFT:
                new_apple['x'] -= 1
            elif apple_direction == RIGHT:
                new_apple['x'] += 1
            # 检查边界与障碍
            if (0 <= new_apple['x'] < CELL_WIDTH and 0 <= new_apple['y'] < CELL_HEIGHT) and \
               not any(obs['x'] == new_apple['x'] and obs['y'] == new_apple['y'] for obs in obstacles):
                apple = new_apple

            # 蛇自动朝苹果移动
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
                # 出界则本帧不动
                if not (0 <= head['x'] < CELL_WIDTH and 0 <= head['y'] < CELL_HEIGHT):
                    new_head = snake_coords[0].copy()
                else:
                    new_head = head
                    # 自身碰撞
                    if new_head in snake_coords[1:]:
                        game_over(screen, clock, collision_sound)
                        return "MENU", coin_count
            else:
                new_head = snake_coords[0].copy()

            if new_head != snake_coords[0]:
                snake_coords.insert(0, new_head)
                # 吃到苹果
                if new_head['x'] == apple['x'] and new_head['y'] == apple['y']:
                    apple_eat_sound.play()
                    coin_count += 10
                    apple = get_random_location(obstacles)
                else:
                    snake_coords.pop()

            # 绘制游戏画面
            screen.fill(BLACK)
            draw_obstacles(screen, obstacles)
            snake_color = SKIN_COLORS[selected_skin]
            draw_snake(screen, snake_coords, snake_color)
            apple_pixel = {'x': apple['x'] * CELL_SIZE, 'y': apple['y'] * CELL_SIZE}
            draw_apple(screen, apple_pixel)
            draw_overlay_menu(screen, overlay_font, muted)
            pygame.display.update()
            clock.tick(16)
        
        if restart_pressed:
            continue  # 重新开始 Apple 模式回合

# --------------------- 2 Players 模式 ---------------------
def game_loop_2players(screen, clock, apple_eat_sound, collision_sound, snake_eaten_sound,
                        coin_count, purchased_skins, selected_skin):
    """
    2 Players 模式：
      - 第一阶段：抢 apple 阶段，两位玩家各自控制一条蛇抢 apple，每吃到 apple 加长一格。
      - 当累计吃到 5 个 apple 后，进入第二阶段：互吃阶段，此时不再生成 apple。
      - 互吃阶段：当蛇头碰到对方蛇身体时，碰撞方保持增长（即不删除尾部），而被碰撞方去掉一节，并播放“snake 被吃”的音效；
        当任一玩家只剩 1 格时，游戏结束。
      - 蛇碰到自身时，游戏继续。
      - 两条蛇均在蛇头位置显示粗线笑脸。
    """
    global muted
    while True:  # 外层循环支持重启
        restart_pressed = False
        # 初始化两条蛇：初始位置稍有区分
        snake1_coords = [{'x': 5, 'y': 10}, {'x': 4, 'y': 10}, {'x': 3, 'y': 10}]
        snake2_coords = [{'x': CELL_WIDTH - 6, 'y': 10}, {'x': CELL_WIDTH - 5, 'y': 10}, {'x': CELL_WIDTH - 4, 'y': 10}]
        direction1 = RIGHT   # 玩家1使用方向键控制
        direction2 = LEFT    # 玩家2使用 WASD 控制
        apple = get_random_location()  # 第一阶段使用 apple
        apple_count = 0  # 记录累计吃到的 apple 数量
        phase = 1  # 1 表示抢 apple 阶段，2 表示互吃阶段
        overlay_font = pygame.font.SysFont(None, 24)

        running = True
        while running:
            # 处理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                elif event.type == pygame.KEYDOWN:
                    # 玩家1：方向键控制
                    if event.key == pygame.K_UP:
                        direction1 = UP
                    elif event.key == pygame.K_DOWN:
                        direction1 = DOWN
                    elif event.key == pygame.K_LEFT:
                        direction1 = LEFT
                    elif event.key == pygame.K_RIGHT:
                        direction1 = RIGHT
                    # 玩家2：WASD 控制
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
                        running = False
                        return "MENU", coin_count
                    elif OVERLAY_VOLUME_RECT.collidepoint(pos):
                        muted = not muted
                        apple_eat_sound.set_volume(0 if muted else 1)
                        collision_sound.set_volume(0 if muted else 1)
                        snake_eaten_sound.set_volume(0 if muted else 1)
            if not running:
                break

            # 计算两蛇新头位置
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

            # 出界检查
            if not (0 <= new_head1['x'] < CELL_WIDTH and 0 <= new_head1['y'] < CELL_HEIGHT):
                game_over(screen, clock, collision_sound)
                return "MENU", coin_count
            if not (0 <= new_head2['x'] < CELL_WIDTH and 0 <= new_head2['y'] < CELL_HEIGHT):
                game_over(screen, clock, collision_sound)
                return "MENU", coin_count

            if phase == 1:
                # 第一阶段：抢 apple 阶段
                snake1_grow = False
                snake2_grow = False
                # 检查玩家1是否吃到 apple
                if new_head1['x'] == apple['x'] and new_head1['y'] == apple['y']:
                    snake1_grow = True
                    apple_eat_sound.play()
                    apple_count += 1
                    apple = get_random_location()
                # 检查玩家2是否吃到 apple
                if new_head2['x'] == apple['x'] and new_head2['y'] == apple['y']:
                    snake2_grow = True
                    apple_eat_sound.play()
                    apple_count += 1
                    apple = get_random_location()

                # 更新两蛇：吃到 apple 时不删除尾部，否则删除尾部保持长度
                snake1_coords.insert(0, new_head1)
                snake2_coords.insert(0, new_head2)
                if not snake1_grow:
                    snake1_coords.pop()
                if not snake2_grow:
                    snake2_coords.pop()

                # 当累计吃到 5 个 apple 后，进入第二阶段
                if apple_count >= 5:
                    phase = 2
            else:
                # 第二阶段：互吃阶段，不再生成 apple
                snake1_coords.insert(0, new_head1)
                snake2_coords.insert(0, new_head2)
                collision1 = False
                collision2 = False
                # 检查玩家1的头是否碰到玩家2的身体（排除头部）
                for seg in snake2_coords[1:]:
                    if new_head1['x'] == seg['x'] and new_head1['y'] == seg['y']:
                        collision1 = True
                        break
                # 检查玩家2的头是否碰到玩家1的身体（排除头部）
                for seg in snake1_coords[1:]:
                    if new_head2['x'] == seg['x'] and new_head2['y'] == seg['y']:
                        collision2 = True
                        break

                # 若发生碰撞，则碰撞方保持增长，被碰撞方去掉一节，并播放音效
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

                # 检查游戏结束条件：任一玩家只剩 1 格时，游戏结束
                if len(snake1_coords) <= 1 or len(snake2_coords) <= 1:
                    game_over(screen, clock, collision_sound)
                    return "MENU", coin_count

            # 绘制画面
            screen.fill(BLACK)
            if phase == 1:
                apple_pixel = {'x': apple['x'] * CELL_SIZE, 'y': apple['y'] * CELL_SIZE}
                draw_apple(screen, apple_pixel)
            # 为区分两玩家，玩家1使用选定皮肤颜色，玩家2使用固定颜色（例如 SKIN_COLORS[0]）
            snake1_color = SKIN_COLORS[selected_skin]
            snake2_color = SKIN_COLORS[0]
            draw_snake(screen, snake1_coords, snake1_color)
            draw_snake(screen, snake2_coords, snake2_color)
            draw_overlay_menu(screen, overlay_font, muted)

            # 显示阶段信息
            info_font = pygame.font.SysFont(None, 24)
            if phase == 1:
                info_text = info_font.render(f"Phase 1: {apple_count} apple(s) eaten", True, WHITE)
            else:
                info_text = info_font.render("Phase 2: Mutual Eating", True, WHITE)
            screen.blit(info_text, (WINDOW_WIDTH//2 - 100, 20))

            pygame.display.update()
            clock.tick(16)
        if restart_pressed:
            continue  # 重新开始本局

# --------------------- 皮肤商店（展示后再购买） ---------------------
def skins_loop(screen, clock, font_button, coin_count, purchased_skins, selected_skin):
    """
    皮肤商店界面：展示 20 种颜色，并在右侧展示预览效果。
      - 点击皮肤方块后，更新右侧预览显示
      - 如果当前预览皮肤尚未购买且金币足够，则在预览区显示 "Purchase" 按钮
      - 点击 "Purchase" 按钮后弹出确认对话框，确认后扣除 100 币并购买该皮肤
    返回 (state, coin_count, purchased_skins, selected_skin)
    """
    confirm_purchase_skin = None  # None 表示没有弹出确认对话框
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "MENU", coin_count, purchased_skins, selected_skin
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                # 若已有确认对话框，则先处理对话框点击
                if confirm_purchase_skin is not None:
                    CONFIRM_WIDTH = 400
                    CONFIRM_HEIGHT = 200
                    confirm_rect = pygame.Rect((WINDOW_WIDTH - CONFIRM_WIDTH) // 2, (WINDOW_HEIGHT - CONFIRM_HEIGHT) // 2, CONFIRM_WIDTH, CONFIRM_HEIGHT)
                    yes_rect = pygame.Rect(confirm_rect.x + 50, confirm_rect.y + CONFIRM_HEIGHT - 60, 100, 40)
                    no_rect = pygame.Rect(confirm_rect.x + CONFIRM_WIDTH - 150, confirm_rect.y + CONFIRM_HEIGHT - 60, 100, 40)
                    if yes_rect.collidepoint(mx, my):
                        coin_count -= 100
                        purchased_skins[confirm_purchase_skin] = True
                        selected_skin = confirm_purchase_skin
                        confirm_purchase_skin = None
                    elif no_rect.collidepoint(mx, my):
                        confirm_purchase_skin = None
                else:
                    # 检查预览区的 Purchase 按钮点击
                    preview_area = pygame.Rect(600, 150, 300, 300)
                    if not purchased_skins[selected_skin] and coin_count >= 100:
                        purchase_button_rect = pygame.Rect(preview_area.x + (preview_area.width - 120)//2, preview_area.y + preview_area.height + 20, 120, 40)
                        if purchase_button_rect.collidepoint(mx, my):
                            confirm_purchase_skin = selected_skin
                            continue
                    # 检查皮肤方块点击，更新预览
                    padding = 20
                    box_size = 40
                    start_x = 50
                    start_y = 150
                    for i, color in enumerate(SKIN_COLORS):
                        row = i // 4
                        col = i % 4
                        bx = start_x + col * (box_size + padding)
                        by = start_y + row * (box_size + padding)
                        rect = pygame.Rect(bx, by, box_size, box_size)
                        if rect.collidepoint(mx, my):
                            selected_skin = i
                            break
                    # 检查返回菜单按钮点击
                    back_text = font_button.render("Back to Menu", True, WHITE)
                    back_rect = back_text.get_rect(topleft=(50, 650))
                    if back_rect.inflate(20, 10).collidepoint(mx, my):
                        return "MENU", coin_count, purchased_skins, selected_skin

        screen.fill(BLACK)

        # 显示标题
        title_font = pygame.font.SysFont(None, 48)
        title_text = title_font.render("Skins Shop", True, WHITE)
        screen.blit(title_text, (50, 50))

        # 显示当前金币
        coin_text = font_button.render(f"Coins: {coin_count}", True, GOLD)
        screen.blit(coin_text, (WINDOW_WIDTH - 200, 50))

        # 绘制皮肤方块
        padding = 20
        box_size = 40
        start_x = 50
        start_y = 150
        label_font = pygame.font.SysFont(None, 24)
        for i, color in enumerate(SKIN_COLORS):
            row = i // 4
            col = i % 4
            bx = start_x + col * (box_size + padding)
            by = start_y + row * (box_size + padding)
            rect = pygame.Rect(bx, by, box_size, box_size)
            pygame.draw.rect(screen, color, rect)
            # 显示 "Owned" 或 "100 coins"
            if purchased_skins[i]:
                label = label_font.render("Owned", True, WHITE)
            else:
                label = label_font.render("100 coins", True, WHITE)
            label_rect = label.get_rect(center=(bx + box_size/2, by + box_size + 12))
            screen.blit(label, label_rect)
            # 如果该皮肤被选中，则绘制白色边框
            if i == selected_skin:
                pygame.draw.rect(screen, WHITE, rect, 3)

        # 绘制右侧预览区域
        preview_area = pygame.Rect(600, 150, 300, 300)
        pygame.draw.rect(screen, GRAY, preview_area, 2)
        preview_title = label_font.render("Preview", True, WHITE)
        preview_title_rect = preview_title.get_rect(center=(preview_area.centerx, preview_area.y - 20))
        screen.blit(preview_title, preview_title_rect)
        # 绘制预览区的蛇示例
        preview_segment_size = 40
        spacing = 10
        total_width = 3 * preview_segment_size + 2 * spacing
        start_preview_x = preview_area.x + (preview_area.width - total_width) // 2
        start_preview_y = preview_area.y + (preview_area.height - preview_segment_size) // 2
        for i in range(3):
            seg_rect = pygame.Rect(start_preview_x + i*(preview_segment_size + spacing), start_preview_y, preview_segment_size, preview_segment_size)
            pygame.draw.rect(screen, SKIN_COLORS[selected_skin], seg_rect)
            pygame.draw.rect(screen, WHITE, seg_rect, 2)
        # 如果当前预览皮肤未购买且金币足够，显示 Purchase 按钮
        if not purchased_skins[selected_skin] and coin_count >= 100:
            purchase_button_rect = pygame.Rect(preview_area.x + (preview_area.width - 120)//2, preview_area.y + preview_area.height + 20, 120, 40)
            pygame.draw.rect(screen, WHITE, purchase_button_rect, 2)
            purchase_text = label_font.render("Purchase", True, WHITE)
            purchase_text_rect = purchase_text.get_rect(center=purchase_button_rect.center)
            screen.blit(purchase_text, purchase_text_rect)
        elif not purchased_skins[selected_skin]:
            insufficient_text = label_font.render("Not enough coins", True, RED)
            insufficient_text_rect = insufficient_text.get_rect(center=(preview_area.centerx, preview_area.y + preview_area.height + 20))
            screen.blit(insufficient_text, insufficient_text_rect)

        # 绘制返回菜单按钮
        back_text = font_button.render("Back to Menu", True, WHITE)
        back_rect = back_text.get_rect(topleft=(50, 650))
        pygame.draw.rect(screen, WHITE, back_rect.inflate(20,10), 2)
        screen.blit(back_text, back_rect)

        # 如果需要显示确认购买对话框，则绘制对话框
        if confirm_purchase_skin is not None:
            CONFIRM_WIDTH = 400
            CONFIRM_HEIGHT = 200
            confirm_rect = pygame.Rect((WINDOW_WIDTH - CONFIRM_WIDTH) // 2, (WINDOW_HEIGHT - CONFIRM_HEIGHT) // 2, CONFIRM_WIDTH, CONFIRM_HEIGHT)
            pygame.draw.rect(screen, GRAY, confirm_rect)
            pygame.draw.rect(screen, WHITE, confirm_rect, 2)
            confirm_font = pygame.font.SysFont(None, 36)
            confirm_text = confirm_font.render("Purchase for 100 coins?", True, WHITE)
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

# --------------------- 菜单 ---------------------
def menu_loop(screen, clock, font_title, font_button, game_start_sound,
              coin_count, purchased_skins, selected_skin):
    """
    菜单界面，包含：
      - “Play as Snake”
      - “Play as Apple”
      - “2 Players Mode”
      - “Skins”
      - “Quit Game”
    右上角显示金币。
    """
    while True:
        # 绘制各菜单按钮文本
        snake_text = font_button.render("Play as Snake", True, WHITE)
        apple_text = font_button.render("Play as Apple", True, WHITE)
        two_players_text = font_button.render("2 Players Mode", True, WHITE)
        skin_text  = font_button.render("Skins", True, WHITE)
        quit_text  = font_button.render("Quit Game", True, WHITE)
        coin_text  = font_button.render(f"Coins: {coin_count}", True, GOLD)

        # 计算各按钮的矩形区域（可根据需要调整位置）
        snake_rect = snake_text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2 - 100))
        apple_rect = apple_text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2 - 40))
        two_players_rect = two_players_text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2 + 20))
        skin_rect  = skin_text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2 + 80))
        quit_rect  = quit_text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2 + 140))
        title_text = font_title.render("Snake Game", True, WHITE)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/3))
        coin_rect = coin_text.get_rect(topright=(WINDOW_WIDTH - 20, 20))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if snake_rect.collidepoint(mx, my):
                    game_start_sound.play()
                    return "SNAKE", coin_count, purchased_skins, selected_skin
                elif apple_rect.collidepoint(mx, my):
                    game_start_sound.play()
                    return "APPLE", coin_count, purchased_skins, selected_skin
                elif two_players_rect.collidepoint(mx, my):
                    game_start_sound.play()
                    return "2PLAYERS", coin_count, purchased_skins, selected_skin
                elif skin_rect.collidepoint(mx, my):
                    game_start_sound.play()
                    return "SKINS", coin_count, purchased_skins, selected_skin
                elif quit_rect.collidepoint(mx, my):
                    pygame.quit(); sys.exit()

        screen.fill(BLACK)
        screen.blit(title_text, title_rect)
        for text, rect in [(snake_text, snake_rect),
                           (apple_text, apple_rect),
                           (two_players_text, two_players_rect),
                           (skin_text,  skin_rect),
                           (quit_text,  quit_rect)]:
            pygame.draw.rect(screen, WHITE, rect.inflate(20, 10), 2)
            screen.blit(text, rect)
        screen.blit(coin_text, coin_rect)
        pygame.display.update()
        clock.tick(15)

# --------------------- 主函数 ---------------------
def main():
    pygame.init()
    pygame.mixer.init()

    # 加载音效
    game_start_sound = pygame.mixer.Sound("game_start.wav")
    apple_eat_sound  = pygame.mixer.Sound("eat_apple.wav")
    collision_sound  = pygame.mixer.Sound("game_over.wav")
    snake_eaten_sound = pygame.mixer.Sound("snake_eaten.wav")  # 新增的音效

    # 根据当前静音状态设置音量
    game_start_sound.set_volume(0 if muted else 1)
    apple_eat_sound.set_volume(0 if muted else 1)
    collision_sound.set_volume(0 if muted else 1)
    snake_eaten_sound.set_volume(0 if muted else 1)

    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Ian's Snake Game")

    font_title  = pygame.font.SysFont(None, 48)
    font_button = pygame.font.SysFont(None, 36)

    # 初始化金币数量、皮肤购买状态、选定皮肤
    coin_count = 1000
    purchased_skins = [False] * 20
    purchased_skins[1] = True  # 例如绿色（下标1）默认已拥有
    selected_skin = 1          # 默认绿色

    state = "MENU"
    while True:
        if state == "MENU":
            state, coin_count, purchased_skins, selected_skin = menu_loop(
                screen, clock, font_title, font_button, game_start_sound,
                coin_count, purchased_skins, selected_skin
            )
        elif state == "SKINS":
            state, coin_count, purchased_skins, selected_skin = skins_loop(
                screen, clock, font_button, coin_count, purchased_skins, selected_skin
            )
        elif state == "SNAKE":
            state, coin_count = game_loop(
                screen, clock, apple_eat_sound, collision_sound,
                coin_count, purchased_skins, selected_skin
            )
        elif state == "APPLE":
            state, coin_count = game_loop_apple(
                screen, clock, apple_eat_sound, collision_sound,
                coin_count, purchased_skins, selected_skin
            )
        elif state == "2PLAYERS":
            state, coin_count = game_loop_2players(
                screen, clock, apple_eat_sound, collision_sound, snake_eaten_sound,
                coin_count, purchased_skins, selected_skin
            )

if __name__ == "__main__":
    main()
