from random import randint

import pygame

pygame.init()

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Цвет камня
STONE_COLOR = (128, 128, 128)

# Скорость движения змейки:
SPEED = 10

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Snake')

# Настройка времени:
clock = pygame.time.Clock()


class GameObject:
    """Родительский класс для объектов игры."""

    def __init__(self, body_color: tuple[int, int, int] = (
            255, 255, 255)) -> None:
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.body_color = body_color

    def draw(self) -> None:
        """Метод отрисовки объекта на игровом поле."""
        raise NotImplementedError

    def draw_cell(self, position: tuple[int, int]) -> None:
        """Метод отрисовки ячейки игровых объектов"""
        rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

    def randomize_position(self,
                           occupied_positions: list[tuple[int, int]]) -> None:
        """Метод для случайного размещения объекта на игровом поле."""
        while True:
            new_position = (randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                            randint(0, GRID_HEIGHT - 1) * GRID_SIZE)
            if new_position not in occupied_positions:
                self.position = new_position
                return


class Apple(GameObject):
    """Класс яблока."""

    def __init__(self, occupied_positions: list[
            tuple[int, int]] | None = None, body_color: tuple[
                int, int, int] = APPLE_COLOR) -> None:
        super().__init__(body_color)
        if occupied_positions is None:
            occupied_positions = []
        self.randomize_position(occupied_positions)

    def draw(self) -> None:
        """Метод отрисовки яблока на игровом поле."""
        self.draw_cell(self.position)


class Stone(GameObject):
    """Класс камня."""

    def __init__(self, occupied_positions: list[tuple[int, int]] | None = None,
                 body_color: tuple[int, int, int] = STONE_COLOR) -> None:
        super().__init__(body_color)
        if occupied_positions is None:
            occupied_positions = []
        self.randomize_position(occupied_positions)

    def draw(self) -> None:
        """Метод отрисовки камня на игровом поле."""
        self.draw_cell(self.position)


class Snake(GameObject):
    """Класс змейки."""

    def __init__(self, body_color: tuple[int, int, int] = SNAKE_COLOR) -> None:
        super().__init__(body_color)
        self.reset()
        self.body_color = SNAKE_COLOR
        self.last: tuple[int, int] | None = None

    def reset(self) -> None:
        """Метод сброса змейки."""
        self.length = 1
        self.positions = [(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None

    def draw(self) -> None:
        """Метод отрисовки змейки на игровом поле."""
        for position in self.positions:
            self.draw_cell(position)
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def get_head_position(self) -> tuple[int, int]:
        """Метод получения позиции головы змейки."""
        return self.positions[0]

    def move(self) -> None:
        """Метод движения змейки."""
        current_head = self.get_head_position()
        x, y = self.direction
        new = ((current_head[0] + (x * GRID_SIZE)) % SCREEN_WIDTH,
               (current_head[1] + (y * GRID_SIZE)) % SCREEN_HEIGHT)
        self.positions.insert(0, new)
        if len(self.positions) > self.length:
            self.last = self.positions.pop()

    def update_direction(self) -> None:
        """Метод обновления направления после нажатия на кнопку."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None


def main():
    """Главная функция игры."""
    snake = Snake()
    apple = Apple(snake.positions)
    stones = []
    score = 0
    while True:
        clock.tick(SPEED + score // 5)
        handle_keys(snake)
        snake.update_direction()
        snake.move()
        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position((snake.positions + [
                s.position for s in stones]))
            score += 1
            if score % 5 == 0:
                stones.append(Stone(snake.positions + [apple.position] + [
                    s.position for s in stones]))
        if snake.get_head_position() in snake.positions[1:]:
            score = 0
            snake.reset()
            apple = Apple(snake.positions)
            stones.clear()
        for stone in stones:
            if snake.get_head_position() == stone.position:
                score = 0
                snake.reset()
                apple = Apple(snake.positions)
                stones.clear()
        screen.fill(BOARD_BACKGROUND_COLOR)
        snake.draw()
        apple.draw()
        for stone in stones:
            stone.draw()
        pygame.display.update()


def handle_keys(game_object) -> None:
    """Функция обработки действий пользователя."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


if __name__ == '__main__':
    main()
