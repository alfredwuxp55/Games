import pygame, sys, random

# Window and grid dimensions
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 800
CELL_SIZE = 20
CELL_WIDTH = WINDOW_WIDTH // CELL_SIZE  # e.g. 50
CELL_HEIGHT = WINDOW_HEIGHT // CELL_SIZE  # e.g. 40

# Color definitions
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED   = (255, 0, 0)
GRAY  = (128, 128, 128)  # obstacles color

# Direction definitions
UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

def draw_snake(surface, snake_coords):
    """Draws the snake on the grid."""
    for coord in snake_coords:
        x = coord['x'] * CELL_SIZE
        y = coord['y'] * CELL_SIZE
        segment = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(surface, GREEN, segment)

def draw_apple(surface, apple):
    """Draws the apple (expects pixel coordinates)."""
    rect = pygame.Rect(int(apple['x']), int(apple['y']), CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(surface, RED, rect)

def draw_obstacles(surface, obstacles):
    """Draws all obstacles on the grid."""
    for obs in obstacles:
        x = obs['x'] * CELL_SIZE
        y = obs['y'] * CELL_SIZE
        rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(surface, GRAY, rect)

def create_obstacles():
    """
    Randomly generates many short obstacles:
      - Generates 30 obstacle segments, each of length 1 to 2 cells.
      - Avoids the safe area (top-left 10x10 grid) where the snake starts.
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
    """
    Generates a random grid location.
    If obstacles is provided, ensures the location is not on an obstacle.
    """
    while True:
        loc = {'x': random.randint(0, CELL_WIDTH - 1), 'y': random.randint(0, CELL_HEIGHT - 1)}
        if obstacles and any(loc['x'] == obs['x'] and loc['y'] == obs['y'] for obs in obstacles):
            continue
        return loc

def update_apple_position(apple, snake_coords, obstacles):
    """
    (Used in snake mode)
    With a 50% chance per frame, the apple attempts to move one cell in a random direction,
    provided the target cell is within bounds and not occupied by the snake or an obstacle.
    """
    if random.random() < 0.5:
        moves = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        random.shuffle(moves)
        for move in moves:
            new_x = apple['x'] + move[0]
            new_y = apple['y'] + move[1]
            if not (0 <= new_x < CELL_WIDTH and 0 <= new_y < CELL_HEIGHT):
                continue
            if any(segment['x'] == new_x and segment['y'] == new_y for segment in snake_coords):
                continue
            if any(obs['x'] == new_x and obs['y'] == new_y for obs in obstacles):
                continue
            apple['x'] = new_x
            apple['y'] = new_y
            break
    return apple

def game_over(screen, clock, collision_sound):
    """Displays Game Over message (for boundary, self-collision, etc.) and then returns to menu."""
    collision_sound.play()
    font_over = pygame.font.SysFont(None, 48)
    text = font_over.render("Game Over", True, RED)
    rect = text.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
    screen.fill(BLACK)
    screen.blit(text, rect)
    pygame.display.update()
    pygame.time.wait(2000)

def game_loop(screen, clock, apple_eat_sound, collision_sound):
    """
    Snake mode: The player controls the snake and the apple moves randomly.
    When the snake eats the apple, the snake grows and the apple respawns.
    Obstacles are present; if the snake's next cell is an obstacle, the snake stays in place.
    The snake can move in all four directions (no 180° reversal protection).
    """
    snake_coords = [
        {'x': 3, 'y': 5},
        {'x': 2, 'y': 5},
        {'x': 1, 'y': 5}
    ]
    direction = RIGHT
    obstacles = create_obstacles()
    apple = get_random_location(obstacles)  # apple in grid coordinates

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                # Accept all four directions
                if event.key == pygame.K_UP:
                    direction = UP
                elif event.key == pygame.K_DOWN:
                    direction = DOWN
                elif event.key == pygame.K_LEFT:
                    direction = LEFT
                elif event.key == pygame.K_RIGHT:
                    direction = RIGHT

        # Calculate desired new head position
        proposed_head = snake_coords[0].copy()
        if direction == UP:
            proposed_head['y'] -= 1
        elif direction == DOWN:
            proposed_head['y'] += 1
        elif direction == LEFT:
            proposed_head['x'] -= 1
        elif direction == RIGHT:
            proposed_head['x'] += 1

        if not (0 <= proposed_head['x'] < CELL_WIDTH and 0 <= proposed_head['y'] < CELL_HEIGHT):
            game_over(screen, clock, collision_sound)
            return "MENU"

        # Check if the new head would hit an obstacle
        if any(obs['x'] == proposed_head['x'] and obs['y'] == proposed_head['y'] for obs in obstacles):
            new_head = snake_coords[0].copy()  # Do not move this frame
        else:
            new_head = proposed_head
            # Game over if the snake's head touches its body
            if new_head in snake_coords[1:]:
                game_over(screen, clock, collision_sound)
                return "MENU"

        # Update snake movement: if moving, insert new head.
        if new_head != snake_coords[0]:
            snake_coords.insert(0, new_head)
            # If snake eats apple, grow (do not remove tail) and respawn apple.
            if new_head['x'] == apple['x'] and new_head['y'] == apple['y']:
                apple_eat_sound.play()
                apple = get_random_location(obstacles)
            else:
                snake_coords.pop()

        # Apple moves randomly (discrete movement)
        apple = update_apple_position(apple, snake_coords, obstacles)

        screen.fill(BLACK)
        draw_obstacles(screen, obstacles)
        draw_snake(screen, snake_coords)
        # Convert apple grid coordinate to pixel coordinate for drawing
        apple_pixel = {'x': apple['x'] * CELL_SIZE, 'y': apple['y'] * CELL_SIZE}
        draw_apple(screen, apple_pixel)
        pygame.display.update()
        clock.tick(16)

def get_snake_direction(snake_coords, apple, obstacles):
    """
    Simple AI: Returns a direction (UP, DOWN, LEFT, RIGHT) for the snake to move toward the apple,
    avoiding obstacles and self-collision. The apple parameter is in grid coordinates.
    If no safe direction exists, returns None.
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

def game_loop_apple(screen, clock, apple_eat_sound, collision_sound):
    """
    Apple mode: The player controls the apple (discrete movement) and it moves continuously
    in its current direction, while the snake is controlled by AI to chase the apple.
    
    - The player's arrow key press updates the apple's moving direction.
    - The apple moves one cell per frame in that direction.
    - When the snake's head reaches the apple, the snake grows (its tail is not removed)
      and the apple respawns.
    - Additionally, if the snake's head touches its body, the game ends.
    """
    snake_coords = [
        {'x': 3, 'y': 5},
        {'x': 2, 'y': 5},
        {'x': 1, 'y': 5}
    ]
    obstacles = create_obstacles()
    apple = get_random_location(obstacles)  # apple stored in grid coordinates
    apple_direction = RIGHT  # initial apple direction

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                # Update apple direction based on player's input
                if event.key == pygame.K_UP:
                    apple_direction = UP
                elif event.key == pygame.K_DOWN:
                    apple_direction = DOWN
                elif event.key == pygame.K_LEFT:
                    apple_direction = LEFT
                elif event.key == pygame.K_RIGHT:
                    apple_direction = RIGHT

        # Continuously move the apple in the current direction
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

        # Snake AI movement toward the apple
        snake_direction = get_snake_direction(snake_coords, apple, obstacles)
        if snake_direction:
            proposed_head = snake_coords[0].copy()
            if snake_direction == UP:
                proposed_head['y'] -= 1
            elif snake_direction == DOWN:
                proposed_head['y'] += 1
            elif snake_direction == LEFT:
                proposed_head['x'] -= 1
            elif snake_direction == RIGHT:
                proposed_head['x'] += 1
            if not (0 <= proposed_head['x'] < CELL_WIDTH and 0 <= proposed_head['y'] < CELL_HEIGHT):
                new_head = snake_coords[0].copy()
            else:
                new_head = proposed_head
                # Check self-collision: if the new head touches any part of the body, game over.
                if new_head in snake_coords[1:]:
                    game_over(screen, clock, collision_sound)
                    return "MENU"
        else:
            new_head = snake_coords[0].copy()

        if new_head != snake_coords[0]:
            snake_coords.insert(0, new_head)
            # If snake catches the apple, grow (do not remove tail) and respawn apple.
            if new_head['x'] == apple['x'] and new_head['y'] == apple['y']:
                apple_eat_sound.play()
                apple = get_random_location(obstacles)
            else:
                snake_coords.pop()

        screen.fill(BLACK)
        draw_obstacles(screen, obstacles)
        draw_snake(screen, snake_coords)
        # Convert apple grid coordinate to pixel coordinate for drawing
        apple_pixel = {'x': apple['x'] * CELL_SIZE, 'y': apple['y'] * CELL_SIZE}
        draw_apple(screen, apple_pixel)
        pygame.display.update()
        clock.tick(16)

def menu_loop(screen, clock, font_title, font_button, game_start_sound):
    """
    Displays the menu allowing the player to choose between:
      "Play as Snake" or "Play as Apple".
    """
    while True:
        snake_text = font_button.render("Play as Snake", True, WHITE)
        apple_text = font_button.render("Play as Apple", True, WHITE)
        snake_button_rect = snake_text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2 - 40))
        apple_button_rect = apple_text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2 + 40))
        title_text = font_title.render("Snake Game", True, WHITE)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/3))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if snake_button_rect.collidepoint(mouse_pos):
                    game_start_sound.play()
                    return "SNAKE"
                elif apple_button_rect.collidepoint(mouse_pos):
                    game_start_sound.play()
                    return "APPLE"

        screen.fill(BLACK)
        screen.blit(title_text, title_rect)
        pygame.draw.rect(screen, WHITE, snake_button_rect.inflate(20, 10), 2)
        pygame.draw.rect(screen, WHITE, apple_button_rect.inflate(20, 10), 2)
        screen.blit(snake_text, snake_button_rect)
        screen.blit(apple_text, apple_button_rect)
        pygame.display.update()
        clock.tick(15)

def main():
    pygame.init()
    pygame.mixer.init()  # Initialize mixer

    # Load sound files (ensure they are in the same directory)
    game_start_sound = pygame.mixer.Sound("game_start.wav")
    apple_eat_sound = pygame.mixer.Sound("eat_apple.wav")
    collision_sound = pygame.mixer.Sound("game_over.wav")

    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Ian's Snake Game")

    font_title = pygame.font.SysFont(None, 48)
    font_button = pygame.font.SysFont(None, 36)

    state = "MENU"
    while True:
        if state == "MENU":
            mode = menu_loop(screen, clock, font_title, font_button, game_start_sound)
            if mode == "SNAKE":
                state = game_loop(screen, clock, apple_eat_sound, collision_sound)
            elif mode == "APPLE":
                state = game_loop_apple(screen, clock, apple_eat_sound, collision_sound)
        # After game over, return to menu (state becomes "MENU")

if __name__ == "__main__":
    main()
