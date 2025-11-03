import random
from enum import Enum

class Direction(Enum):
    UP = 'up'
    DOWN = 'down'
    LEFT = 'left'
    RIGHT = 'right'

class SnakeGame:
    def __init__(self, grid_size=20):
        """
            SnakeGame class constructor
        """
        self.grid_size = grid_size
        self.snake = None
        self.direction = None
        self.food = None
        self.score = None
        self.game_over = None
        self.moves = None
        self.reset()

    def reset(self):
        """
            Initialize a new game
        """
        center = self.grid_size // 2
        self.snake = [(center, center), (center, center+1), (center, center+2)]
        self.direction = Direction.UP
        self.food = self.generate_food()
        self.score = 0
        self.game_over = False
        self.moves = 0

    def generate_food(self):
        """
            Generate food at a random position not occupied by the snake
        """
        while True:
            food = (random.randint(0, self.grid_size - 1), random.randint(0, self.grid_size - 1))
            if food not in self.snake:
                return food

    def change_direction(self, new_direction):
        """
            Change snake direction (preventing 180-degree turns)
        """
        opposite = {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT
        }

        if new_direction != opposite.get(self.direction):
            self.direction = new_direction

    def update(self):
        """
            Update game state for one tick
        """
        if self.game_over:
            return

        # Calculate new head position
        head_x, head_y = self.snake[0]
        if self.direction == Direction.UP:
            new_head = (head_x, head_y - 1)
        elif self.direction == Direction.DOWN:
            new_head = (head_x, head_y + 1)
        elif self.direction == Direction.LEFT:
            new_head = (head_x - 1, head_y)
        elif self.direction == Direction.RIGHT:
            new_head = (head_x + 1, head_y)

        # Check wall collisions
        if new_head[0] < 0 or new_head[0] >= self.grid_size or new_head[1] < 0 or new_head[1] >= self.grid_size:
            self.game_over = True
            return

        # Check self collision
        if new_head in self.snake:
            self.game_over = True
            return

        # Move snake
        self.snake.insert(0, new_head)

        # Check if food has been eaten
        if new_head == self.food:
            self.score += 10
            self.food = self.generate_food()
        else:
            self.snake.pop()        # Remove tail if no food eaten

        self.moves += 1

    def get_state(self):
        """
            Return current game state as a dictionary
        """
        return {
            'snake': self.snake,
            'food': self.food,
            'score': self.score,
            'game_over': self.game_over,
            'direction': self.direction.value,
            'moves': self.moves,
            'grid_size': self.grid_size
        }

    def get_valid_directions(self):
        """
            Returns a list of valid directions (no 180-degree turns)
        """
        opposite = {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT
        }

        return [d for d in Direction if d != opposite.get(self.direction)]