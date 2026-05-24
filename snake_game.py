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
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)

# Типы бонусов
BONUS_EXTRA_LIFE = "extra_life"
BONUS_SPEED_UP = "speed_up"
BONUS_SLOW_DOWN = "slow_down"
BONUS_DOUBLE_POINTS = "double_points"
BONUS_SHIELD = "shield"

# Настройка экрана
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Змейка")
clock = pygame.time.Clock()

# Шрифты
font = pygame.font.Font(None, 36)
big_font = pygame.font.Font(None, 72)
small_font = pygame.font.Font(None, 24)

def draw_text(text, font, color, x, y):
    """Функция для отрисовки текста"""
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)

def draw_text_left(text, font, color, x, y):
    """Функция для отрисовки текста с выравниванием по левому краю"""
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(topleft=(x, y))
    screen.blit(text_surface, text_rect)

def get_bonus_color(bonus_type):
    """Возвращает цвет для типа бонуса"""
    colors = {
        BONUS_EXTRA_LIFE: PURPLE,
        BONUS_SPEED_UP: RED,
        BONUS_SLOW_DOWN: CYAN,
        BONUS_DOUBLE_POINTS: YELLOW,
        BONUS_SHIELD: ORANGE
    }
    return colors.get(bonus_type, WHITE)

def get_bonus_symbol(bonus_type):
    """Возвращает символ для типа бонуса"""
    symbols = {
        BONUS_EXTRA_LIFE: "♥",
        BONUS_SPEED_UP: "⚡",
        BONUS_SLOW_DOWN: "❄",
        BONUS_DOUBLE_POINTS: "2x",
        BONUS_SHIELD: "🛡"
    }
    return symbols.get(bonus_type, "?")

def choose_difficulty():
    """Меню выбора уровня сложности"""
    difficulty = None
    waiting = True
    
    while waiting:
        screen.fill(BLACK)
        draw_text("ВЫБЕРИТЕ СЛОЖНОСТЬ", big_font, GREEN, WIDTH // 2, HEIGHT // 4)
        draw_text("1 - Просто (медленно)", font, WHITE, WIDTH // 2, HEIGHT // 2 - 50)
        draw_text("2 - Легко (быстрее)", font, WHITE, WIDTH // 2, HEIGHT // 2)
        draw_text("3 - Сложно (очень быстро)", font, WHITE, WIDTH // 2, HEIGHT // 2 + 50)
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    difficulty = 8  # Просто - медленно
                    waiting = False
                elif event.key == pygame.K_2:
                    difficulty = 15  # Легко - быстрее
                    waiting = False
                elif event.key == pygame.K_3:
                    difficulty = 25  # Сложно - очень быстро
                    waiting = False
        
        clock.tick(FPS)
    
    return difficulty

def game_loop(snake_speed):
    """Основной цикл игры"""
    # Параметры змейки
    snake_block = 20
    
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
    
    # Жизни
    lives = 3
    max_lives = 5
    
    # Бонусы
    bonus = None
    bonus_x = 0
    bonus_y = 0
    bonus_timer = 0
    bonus_duration = 300  # Длительность действия бонуса в кадрах
    
    # Активные эффекты бонусов
    double_points = False
    double_points_timer = 0
    shield = False
    shield_timer = 0
    base_speed = snake_speed
    
    # Шанс появления бонуса (1 к 20 при поедании еды)
    bonus_chance = 0.05
    
    # Игровой цикл
    running = True
    game_over = False
    
    while running:
        while game_over:
            screen.fill(BLACK)
            draw_text("ИГРА ОКОНЧЕНА!", big_font, RED, WIDTH // 2, HEIGHT // 3)
            draw_text(f"Ваш счет: {score}", font, WHITE, WIDTH // 2, HEIGHT // 2)
            draw_text(f"Осталось жизней: {lives}", font, YELLOW, WIDTH // 2, HEIGHT // 2 + 40)
            if lives > 0:
                draw_text("Нажмите C для продолжения", font, GREEN, WIDTH // 2, HEIGHT * 2 // 3)
            else:
                draw_text("Нажмите Q для выхода или C для новой игры", font, GREEN, WIDTH // 2, HEIGHT * 2 // 3)
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
                        if lives > 0:
                            # Продолжить с текущей игрой
                            snake_x = WIDTH // 2
                            snake_y = HEIGHT // 2
                            dx = 0
                            dy = 0
                            snake_body = []
                            snake_length = 1
                            lives -= 1
                            game_over = False
                            # Сброс бонусов
                            bonus = None
                            double_points = False
                            shield = False
                            snake_speed = base_speed
                        else:
                            # Новая игра
                            snake_speed = choose_difficulty()
                            game_loop(snake_speed)
        
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
            if shield:
                # Щит защищает от удара о стену
                shield = False
                shield_timer = 0
                # Отталкиваем змейку от стены
                if snake_x >= WIDTH:
                    snake_x = WIDTH - snake_block
                elif snake_x < 0:
                    snake_x = 0
                if snake_y >= HEIGHT:
                    snake_y = HEIGHT - snake_block
                elif snake_y < 0:
                    snake_y = 0
            else:
                game_over = True
        
        # Отрисовка фона
        screen.fill(BLACK)
        
        # Отрисовка еды
        pygame.draw.rect(screen, RED, [food_x, food_y, snake_block, snake_block])
        
        # Отрисовка бонуса (если есть)
        if bonus is not None and bonus_timer > 0:
            bonus_color = get_bonus_color(bonus)
            pygame.draw.rect(screen, bonus_color, [bonus_x, bonus_y, snake_block, snake_block])
            # Рисуем символ бонуса
            bonus_text = small_font.render(get_bonus_symbol(bonus), True, BLACK)
            text_rect = bonus_text.get_rect(center=(bonus_x + snake_block//2, bonus_y + snake_block//2))
            screen.blit(bonus_text, text_rect)
            bonus_timer -= 1
        
        # Обновление тела змейки
        snake_head = [snake_x, snake_y]
        snake_body.append(snake_head)
        
        if len(snake_body) > snake_length:
            del snake_body[0]
        
        # Проверка на столкновение с хвостом
        for segment in snake_body[:-1]:
            if segment == snake_head:
                if shield:
                    # Щит защищает от удара о хвост
                    shield = False
                    shield_timer = 0
                    game_over = False
                else:
                    game_over = True
        
        # Отрисовка змейки
        for i, segment in enumerate(snake_body):
            if shield and i == 0:
                # Голова со щитом окрашивается в оранжевый
                color = ORANGE
            elif i == 0:
                color = GREEN  # Голова зеленая
            else:
                color = BLUE  # Тело синее
            pygame.draw.rect(screen, color, [segment[0], segment[1], snake_block, snake_block])
            # Если есть щит, рисуем индикатор вокруг головы
            if shield and i == 0:
                pygame.draw.rect(screen, CYAN, [segment[0]-2, segment[1]-2, snake_block+4, snake_block+4], 2)
        
        # Отрисовка счета и жизней
        draw_text_left(f"Счет: {score}", font, WHITE, 10, 10)
        draw_text_left(f"Жизни: {'♥' * lives}", font, RED, 10, 50)
        
        # Отрисовка активных эффектов
        effect_y = 90
        if double_points:
            draw_text_left(f"2x Очки: {double_points_timer//60}с", small_font, YELLOW, 10, effect_y)
            effect_y += 25
        if shield:
            draw_text_left(f"Щит: {shield_timer//60}с", small_font, ORANGE, 10, effect_y)
            effect_y += 25
        
        pygame.display.flip()
        
        # Поедание еды
        if snake_x == food_x and snake_y == food_y:
            food_x = round(random.randrange(0, WIDTH - snake_block) / snake_block) * snake_block
            food_y = round(random.randrange(0, HEIGHT - snake_block) / snake_block) * snake_block
            snake_length += 1
            
            # Начисление очков с учетом множителя
            points = 10
            if double_points:
                points *= 2
            score += points
            
            # Шанс появления бонуса
            if random.random() < bonus_chance and bonus is None:
                bonus = random.choice([BONUS_EXTRA_LIFE, BONUS_SPEED_UP, BONUS_SLOW_DOWN, BONUS_DOUBLE_POINTS, BONUS_SHIELD])
                bonus_x = round(random.randrange(0, WIDTH - snake_block) / snake_block) * snake_block
                bonus_y = round(random.randrange(0, HEIGHT - snake_block) / snake_block) * snake_block
                bonus_timer = 600  # Бонус исчезнет через 600 кадров (10 секунд)
        
        # Поедание бонуса
        if bonus is not None and snake_x == bonus_x and snake_y == bonus_y:
            # Применяем эффект бонуса
            if bonus == BONUS_EXTRA_LIFE:
                if lives < max_lives:
                    lives += 1
            elif bonus == BONUS_SPEED_UP:
                snake_speed = min(base_speed + 5, 30)  # Увеличиваем скорость, но не более 30
            elif bonus == BONUS_SLOW_DOWN:
                snake_speed = max(base_speed - 3, 5)  # Замедляем, но не менее 5
            elif bonus == BONUS_DOUBLE_POINTS:
                double_points = True
                double_points_timer = 600  # 10 секунд
            elif bonus == BONUS_SHIELD:
                shield = True
                shield_timer = 600  # 10 секунд
            
            bonus = None
        
        # Обновление таймеров эффектов
        if double_points:
            double_points_timer -= 1
            if double_points_timer <= 0:
                double_points = False
        
        if shield:
            shield_timer -= 1
            if shield_timer <= 0:
                shield = False
        
        # Возврат скорости к базовой если она была изменена бонусами
        if bonus != BONUS_SPEED_UP and bonus != BONUS_SLOW_DOWN:
            if snake_speed != base_speed and not double_points and not shield:
                pass  # Скорость остается измененной
        
        clock.tick(snake_speed)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    snake_speed = choose_difficulty()
    game_loop(snake_speed)
