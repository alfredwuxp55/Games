import pygame, sys, random

# Window and grid dimensions
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 800
CELL_SIZE = 20
CELL_WIDTH = WINDOW_WIDTH // CELL_SIZE
CELL_HEIGHT = WINDOW_HEIGHT // CELL_SIZE

# Color definitions
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Direction definitions
UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

def draw_snake(surface, snake_coords):
    """Draws each part of the snake."""
    for coord in snake_coords:
        x = coord['x'] * CELL_SIZE
        y = coord['y'] * CELL_SIZE
        snake_segment = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(surface, GREEN, snake_segment)

def draw_apple(surface, coord):
    """Draws the apple."""
    x = coord['x'] * CELL_SIZE
    y = coord['y'] * CELL_SIZE
    apple = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(surface, RED, apple)

def get_random_location():
    """Generates a random location for the apple."""
    return {'x': random.randint(0, CELL_WIDTH - 1), 'y': random.randint(0, CELL_HEIGHT - 1)}

def game_over(screen, clock):
    """Displays game over message and waits before returning to the menu."""
    font_over = pygame.font.SysFont(None, 48)
    game_over_text = font_over.render("Game Over", True, RED)
    text_rect = game_over_text.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
    screen.fill(BLACK)
    screen.blit(game_over_text, text_rect)
    pygame.display.update()
    pygame.time.wait(2000)

def game_loop(screen, clock):
    """Main game loop for Snake. Returns to the menu on collision."""
    snake_coords = [
        {'x': 3, 'y': 5},
        {'x': 2, 'y': 5},
        {'x': 1, 'y': 5}
    ]
    direction = RIGHT
    apple = get_random_location()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and direction != DOWN:
                    direction = UP
                elif event.key == pygame.K_DOWN and direction != UP:
                    direction = DOWN
                elif event.key == pygame.K_LEFT and direction != RIGHT:
                    direction = LEFT
                elif event.key == pygame.K_RIGHT and direction != LEFT:
                    direction = RIGHT

        head = snake_coords[0].copy()
        if direction == UP:
            head['y'] -= 1
        elif direction == DOWN:
            head['y'] += 1
        elif direction == LEFT:
            head['x'] -= 1
        elif direction == RIGHT:
            head['x'] += 1

        # Check for collision with walls
        if head['x'] < 0 or head['x'] >= CELL_WIDTH or head['y'] < 0 or head['y'] >= CELL_HEIGHT:
            game_over(screen, clock)
            return "MENU"

        # Check for collision with itself
        for segment in snake_coords:
            if segment['x'] == head['x'] and segment['y'] == head['y']:
                game_over(screen, clock)
                return "MENU"

        snake_coords.insert(0, head)
        if head['x'] == apple['x'] and head['y'] == apple['y']:
            apple = get_random_location()
        else:
            snake_coords.pop()

        screen.fill(BLACK)
        draw_snake(screen, snake_coords)
        draw_apple(screen, apple)
        pygame.display.update()
        clock.tick(16)

def menu_loop(screen, clock, font_title, font_button):
    """Menu screen that displays English text and waits for the user to start the game."""
    while True:
        start_text = font_button.render("Start Game", True, WHITE)
        start_button_rect = start_text.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
        button_rect = pygame.Rect(start_button_rect.left - 10, start_button_rect.top - 5,
                                  start_button_rect.width + 20, start_button_rect.height + 10)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if button_rect.collidepoint(mouse_pos):
                    return "GAME"

        screen.fill(BLACK)
        title_text = font_title.render("Snake Game", True, WHITE)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 3))
        screen.blit(title_text, title_rect)

        pygame.draw.rect(screen, BLACK, button_rect)
        pygame.draw.rect(screen, WHITE, button_rect, 2)
        screen.blit(start_text, start_button_rect)

        pygame.display.update()
        clock.tick(15)

def main():
    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Ian's Snake Game")

    font_title = pygame.font.SysFont(None, 48)
    font_button = pygame.font.SysFont(None, 36)

    state = "MENU"
    while True:
        if state == "MENU":
            state = menu_loop(screen, clock, font_title, font_button)
        elif state == "GAME":
            state = game_loop(screen, clock)

if __name__ == "__main__":
    main()
