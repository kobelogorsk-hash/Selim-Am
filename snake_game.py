import pygame
import random
import sys

# Инициализация Pygame
pygame.init()

# Константы
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# Настройка экрана
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Змейка")
clock = pygame.time.Clock()

# Шрифты
font = pygame.font.Font(None, 36)
big_font = pygame.font.Font(None, 72)

def draw_text(text, font, color, x, y):
    """Функция для отрисовки текста"""
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)

def game_loop():
    """Основной цикл игры"""
    # Параметры змейки
    snake_block = 20
    snake_speed = 15
    
    # Начальная позиция змейки
    snake_x = WIDTH // 2
    snake_y = HEIGHT // 2
    
    # Направление движения
    dx = 0
    dy = 0
    
    # Тело змейки
    snake_body = []
    snake_length = 1
    
    # Позиция еды
    food_x = round(random.randrange(0, WIDTH - snake_block) / snake_block) * snake_block
    food_y = round(random.randrange(0, HEIGHT - snake_block) / snake_block) * snake_block
    
    # Счет
    score = 0
    
    # Игровой цикл
    running = True
    game_over = False
    
    while running:
        while game_over:
            screen.fill(BLACK)
            draw_text("ИГРА ОКОНЧЕНА!", big_font, RED, WIDTH // 2, HEIGHT // 3)
            draw_text(f"Ваш счет: {score}", font, WHITE, WIDTH // 2, HEIGHT // 2)
            draw_text("Нажмите Q для выхода или C для повторной игры", font, GREEN, WIDTH // 2, HEIGHT * 2 // 3)
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    game_over = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        running = False
                        game_over = False
                    if event.key == pygame.K_c:
                        game_loop()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Управление змейкой
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and dx != 1:
                    dx = -1
                    dy = 0
                elif event.key == pygame.K_RIGHT and dx != -1:
                    dx = 1
                    dy = 0
                elif event.key == pygame.K_UP and dy != 1:
                    dy = -1
                    dx = 0
                elif event.key == pygame.K_DOWN and dy != -1:
                    dy = 1
                    dx = 0
        
        # Движение змейки
        snake_x += dx * snake_block
        snake_y += dy * snake_block
        
        # Проверка на столкновение со стенами
        if snake_x >= WIDTH or snake_x < 0 or snake_y >= HEIGHT or snake_y < 0:
            game_over = True
        
        # Отрисовка фона
        screen.fill(BLACK)
        
        # Отрисовка еды
        pygame.draw.rect(screen, RED, [food_x, food_y, snake_block, snake_block])
        
        # Обновление тела змейки
        snake_head = [snake_x, snake_y]
        snake_body.append(snake_head)
        
        if len(snake_body) > snake_length:
            del snake_body[0]
        
        # Проверка на столкновение с хвостом
        for segment in snake_body[:-1]:
            if segment == snake_head:
                game_over = True
        
        # Отрисовка змейки
        for i, segment in enumerate(snake_body):
            color = GREEN if i == 0 else BLUE  # Голова зеленая, тело синее
            pygame.draw.rect(screen, color, [segment[0], segment[1], snake_block, snake_block])
        
        # Отрисовка счета
        draw_text(f"Счет: {score}", font, WHITE, 70, 30)
        
        pygame.display.flip()
        
        # Поедание еды
        if snake_x == food_x and snake_y == food_y:
            food_x = round(random.randrange(0, WIDTH - snake_block) / snake_block) * snake_block
            food_y = round(random.randrange(0, HEIGHT - snake_block) / snake_block) * snake_block
            snake_length += 1
            score += 10
        
        clock.tick(snake_speed)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    game_loop()
