from operator import truediv

from pkg_resources import require
from pyasn1.type.tag import initTagSet
from twisted.mail.maildir import initializeMaildir

from game.game_engine import SnakeGame, Direction
import pytest

class TestGameInitialization:
    """
        Test game initialization and reset
    """
    def test_game_initializes_with_correct_grid_size(self):
        game = SnakeGame(grid_size=20)
        assert game.grid_size == 20

    def test_snake_starts_with_three_segments(self):
        game = SnakeGame()
        assert len(game.snake) == 3

    def test_snake_starts_in_center(self):
        game = SnakeGame(grid_size=20)
        center = 20 // 2
        assert game.snake[0] == (center, center)

    def test_initial_direction_is_up(self):
        game = SnakeGame()
        assert game.direction == Direction.UP

    def test_initial_score_is_zero(self):
        game = SnakeGame()
        assert game.score == 0

    def test_game_not_over_at_start(self):
        game = SnakeGame()
        assert game.game_over is False

    def test_food_generates_on_initialization(self):
        game = SnakeGame()
        assert game.food is not None
        assert len(game.food) == 2 # (x, y)

    def test_food_not_on_snake(self):
        game = SnakeGame()
        assert game.food not in game.snake

class TestSnakeMovement:
    """
        Test snake movement mechanics
    """
    def test_snake_moves_up(self):
        game = SnakeGame()
        initial_head = game.snake[0]
        game.direction = Direction.UP
        game.update()

        new_head = game.snake[0]
        assert new_head == (initial_head[0], initial_head[1] - 1)

    def test_snake_moves_down(self):
        game = SnakeGame()
        initial_head = game.snake[0]
        game.direction = Direction.DOWN
        game.update()

        new_head = game.snake[0]
        assert new_head == (initial_head[0], initial_head[1] + 1)

    def test_snake_moves_left(self):
        game = SnakeGame()
        initial_head = game.snake[0]
        game.direction = Direction.LEFT
        game.update()

        new_head = game.snake[0]
        assert new_head == (initial_head[0] - 1, initial_head[1])

    def test_snake_moves_right(self):
        game = SnakeGame()
        initial_head = game.snake[0]
        game.direction = Direction.RIGHT
        game.update()

        new_head = game.snake[0]
        assert new_head == (initial_head[0] + 1, initial_head[1])

    def test_snake_length_stays_same_when_not_eating(self):
        game = SnakeGame()
        initial_length = len(game.snake)
        game.update()
        assert len(game.snake) == initial_length

    def test_moves_counter_increments(self):
        game = SnakeGame()
        assert game.moves == 0
        game.update()
        assert game.moves == 1
        game.update()
        assert game.moves == 2

class TestDirectionChange:
    """
        Test direction change logic
    """
    def test_can_change_from_up_to_left(self):
        game = SnakeGame()
        game.direction = Direction.UP
        game.change_direction(Direction.LEFT)
        assert game.direction == Direction.LEFT

    def test_can_change_from_up_to_right(self):
        game = SnakeGame()
        game.direction = Direction.UP
        game.change_direction(Direction.RIGHT)
        assert game.direction == Direction.RIGHT

    def test_cannot_reverse_up_to_down(self):
        game = SnakeGame()
        game.direction = Direction.UP
        game.change_direction(Direction.DOWN)
        assert game.direction == Direction.UP       # Should stay up

    def test_cannot_reverse_left_to_right(self):
        game = SnakeGame()
        game.direction = Direction.LEFT
        game.change_direction(Direction.RIGHT)
        assert game.direction == Direction.LEFT     # Should stay left

    def test_cannot_reverse_down_to_up(self):
        game = SnakeGame()
        game.direction = Direction.DOWN
        game.change_direction(Direction.UP)
        assert game.direction == Direction.DOWN     # Should stay down

    def test_cannot_reverse_right_to_left(self):
        game = SnakeGame()
        game.direction = Direction.RIGHT
        game.change_direction(Direction.LEFT)
        assert game.direction == Direction.RIGHT    # Should stay right

class TestFoodConsumption:
    """
        Test food eating mechanics
    """
    def test_snake_grows_when_eating_food(self):
        game = SnakeGame()
        initial_length = len(game.snake)
        # Place food directly in front of the snake
        head = game.snake[0]
        game.food = (head[0], head[1] - 1)      # UP direction
        game.direction = Direction.UP
        game.update()
        assert len(game.snake) == initial_length + 1

    def test_score_increases_when_eating_food(self):
        game = SnakeGame()
        initial_score = game.score
        # Place food in front of snake
        head = game.snake[0]
        game.food = (head[0], head[1] - 1)
        game.direction = Direction.UP
        game.update()
        assert game.score == initial_score + 10

    def test_new_food_generates_after_eating(self):
        game = SnakeGame()
        # Place food in front of snake
        head = game.snake[0]
        old_food = (head[0], head[1] - 1)
        game.food = old_food
        game.direction = Direction.UP
        game.update()
        assert game.food != old_food
        assert game.food is not None

class TestCollisionDetection:
    """
        Test collision detection
    """
    def test_game_over_when_hitting_top_wall(self):
        game = SnakeGame(grid_size=20)
        game.snake = [(10, 0), (10, 1), (10, 2)]    # top edge
        game.direction = Direction.UP
        game.update()
        assert game.game_over is True

    def test_game_over_when_hitting_bottom_wall(self):
        game = SnakeGame(grid_size=20)
        game.snake = [(10, 19), (10, 18), (10, 17)] # bottom edge
        game.direction = Direction.DOWN
        game.update()
        assert game.game_over is True

    def test_game_over_when_hitting_left_wall(self):
        game = SnakeGame(grid_size=20)
        game.snake = [(0, 10), (1, 10), (2, 10)]    # left edge
        game.direction = Direction.LEFT
        game.update()
        assert game.game_over is True

    def test_game_over_when_hitting_right_wall(self):
        game = SnakeGame(grid_size=20)
        game.snake = [(19, 10), (18, 10), (17, 10)] # right edge
        game.direction = Direction.RIGHT
        game.update()
        assert game.game_over is True

    def test_game_over_when_hitting_self(self):
        game = SnakeGame()
        # Create scenario where snake will hit itself
        game.snake = [(5, 5), (5, 6), (4, 6), (4, 5)]
        game.direction = Direction.DOWN
        game.update()
        assert game.game_over is True

    def test_no_update_after_game_over(self):
        game = SnakeGame()
        game.game_over = True
        initial_snake = game.snake.copy()
        game.update()
        assert game.snake == initial_snake

class TestGameReset:
    """
        Test game reset functionality
    """
    def test_reset_reinitializes_snake(self):
        game = SnakeGame()
        game.update()
        game.update()
        game.reset()
        assert len(game.snake) == 3

    def test_reset_clears_score(self):
        game = SnakeGame()
        game.score = 100
        game.reset()
        assert game.score == 0

    def test_reset_clears_game_over(self):
        game = SnakeGame()
        game.game_over = True
        game.reset()
        assert game.game_over is False

    def test_reset_clears_moves(self):
        game = SnakeGame()
        game.moves = 50
        game.reset()
        assert game.moves == 0

class TestGameState:
    """
        Test game state export
    """
    def test_get_state_returns_dict(self):
        game = SnakeGame()
        state = game.get_state()
        assert isinstance(state, dict)

    def test_get_state_contains_all_fields(self):
        game = SnakeGame()
        state = game.get_state()
        required_fields = ['snake', 'food', 'score', 'game_over', 'direction', 'moves', 'grid_size']
        for field in required_fields:
            assert field in state

    def test_get_state_direction_is_string(self):
        game = SnakeGame()
        state = game.get_state()
        assert isinstance(state['direction'], str)

    def test_get_valid_directions_excludes_opposite(self):
        game = SnakeGame()
        game.direction = Direction.UP
        valid_dirs = game.get_valid_directions()

        assert Direction.UP in valid_dirs
        assert Direction.LEFT in valid_dirs
        assert Direction.RIGHT in valid_dirs
        assert Direction.DOWN not in valid_dirs # Opposite of UP

class TestEdgeCases:
    """
        Test edge cases and boundary conditions
    """
    def test_food_generation_with_full_board(self):
        # This should not hang or crash
        game = SnakeGame(grid_size=5)
        # Fill most of the board
        game.snake = [(x, y) for x in range(5) for y in range(5)]
        game.snake = game.snake[:-1]    # Leave one spot
        # Should still generate food in remaining spot
        food = game.generate_food()
        assert food not in game.snake

    def test_very_small_grid(self):
        game = SnakeGame(grid_size=5)
        assert game.grid_size == 5
        game.update()
        assert not game.game_over   # Should still work

    def test_multiple_direction_changes_before_update(self):
        game = SnakeGame()
        game.change_direction(Direction.LEFT)
        game.change_direction(Direction.DOWN)
        game.change_direction(Direction.RIGHT)
        # Only last valid change should apply
        assert game.direction == Direction.RIGHT

# Parametrized tests for better coverage
@pytest.mark.parametrize("direction,expected_offset", [
    (Direction.UP, (0, -1)),
    (Direction.DOWN, (0, 1)),
    (Direction.LEFT, (-1, 0)),
    (Direction.RIGHT, (1, 0)),
])

def test_direction_offsets(direction, expected_offset):
    """
        Test that each direction produces correct offset
    """
    game = SnakeGame()
    initial_head = game.snake[0]
    game.direction = direction
    game.update()

    new_head = game.snake[0]
    actual_offset = (new_head[0] - initial_head[0], new_head[1] - initial_head[1])
    assert actual_offset == expected_offset

@pytest.mark.parametrize("grid_size", [10, 20, 30, 50])
def test_different_grid_sizes(grid_size):
    """Test game works with different grid sizes"""
    game = SnakeGame(grid_size=grid_size)
    assert game.grid_size == grid_size
    game.update()
    assert not game.game_over