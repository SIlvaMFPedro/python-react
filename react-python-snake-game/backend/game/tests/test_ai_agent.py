from asyncio import SendfileNotAvailableError
from turtledemo.penrose import start

from numpy.f2py.auxfuncs import isint1

from game.game_engine import Direction
from game.ai_agent import SnakeAI
import pytest

@pytest.fixture
def sample_game_state():
    """
        Fixture providing a sample game state
    """
    return {
        'snake': [(10, 10), (10, 11), (10, 12)],
        'food': (10, 5),
        'direction': 'up',
        'grid_size': 20,
        'score': 0,
        'game_over': False,
        'moves': 0
    }

class TestAIInitialization:
    """
        Test AI agent initialization
    """
    def test_ai_initializes_with_default_strategy(self):
        ai = SnakeAI()
        assert ai.strategy == 'astar'

    def test_ai_initializes_with_simple_strategy(self):
        ai = SnakeAI(strategy='simple')
        assert ai.strategy == 'simple'

    def test_ai_initializes_with_safe_strategy(self):
        ai = SnakeAI(strategy='safe')
        assert ai.strategy == 'safe'

class TestSimpleStrategy:
    """
        Test simple greedy strategy
    """
    def test_simple_strategy_moves_toward_food_vertically(self, sample_game_state):
        ai = SnakeAI(strategy='simple')
        # Food is at (10, 5), snake head at (10, 10)
        # Should move UP toward food
        direction = ai.get_next_move(sample_game_state)
        assert direction == Direction.UP

    def test_simple_strategy_moves_toward_food_horizontally(self, sample_game_state):
        ai = SnakeAI(strategy='simple')
        sample_game_state['food'] = (15, 10)    # Food to the right
        direction = ai.get_next_move(sample_game_state)
        assert direction == Direction.RIGHT

    def test_simple_strategy_returns_valid_direction(self, sample_game_state):
        ai = SnakeAI(strategy='simple')
        direction = ai.get_next_move(sample_game_state)
        assert isinstance(direction, Direction)

    def test_simple_strategy_avoid_walls(self):
        ai = SnakeAI(strategy='simple')
        game_state = {
            'snake': [(0, 10), (1, 10), (2, 10)],   # at left wall
            'food': (0, 5),                         # food also at left wall
            'direction': 'up',
            'grid_size': 20,
            'score': 0,
            'game_over': False,
            'moves': 0,
        }
        direction = ai.get_next_move(game_state)
        # Should not try to move LEFT into a wall
        assert direction != Direction.LEFT

class TestAStarStrategy:
    """
        Test A* pathfinding strategy
    """
    def test_astar_finds_path_to_food(self, sample_game_state):
        ai = SnakeAI(strategy='astar')
        direction = ai.get_next_move(sample_game_state)
        assert isinstance(direction, Direction)

    def test_astar_returns_direction_toward_food(self, sample_game_state):
        ai = SnakeAI(strategy='astar')
        # Food at (10, 5), snake at (10, 10), should move up
        direction = ai.get_next_move(sample_game_state)
        assert direction == Direction.UP

    def test_astar_handles_no_path_gracefully(self, sample_game_state):
        ai = SnakeAI(strategy='astar')
        # Surround food with snake body (no path)
        sample_game_state['food'] = (10, 10)
        sample_game_state['snake'] = [
            (11, 10), (11, 11), (10, 11), (9, 11),
            (9, 10), (9, 9), (10, 9), (11, 9)
        ]
        # Should fallback and return something
        direction = ai.get_next_move(sample_game_state)
        assert isinstance(direction, Direction)

class TestSafeStrategy:
    """
        Test safety-first strategy
    """
    def test_safe_strategy_returns_valid_direction(self, sample_game_state):
        ai = SnakeAI(strategy='safe')
        direction = ai.get_next_move(sample_game_state)
        assert isinstance(direction, Direction)

    def test_safe_strategy_prioritizes_space(self):
        ai = SnakeAI(strategy='safe')
        # Create a situation where one direction has more space
        game_state = {
            'snake': [(10, 10), (10, 11), (10, 12)],
            'food': (10, 5),
            'direction': 'up',
            'grid_size': 20,
            'score': 0,
            'game_over': False,
            'moves': 0,
        }
        direction = ai.get_next_move(game_state)
        assert isinstance(direction, Direction)

class TestPathfinding:
    """
        Test pathfinding algorithms
    """
    def test_astar_search_finds_straight_path(self):
        ai = SnakeAI(strategy='astar')
        start = (5, 5)
        goal = (5, 10)
        snake = [(5, 5), (5, 6), (5, 7)]
        grid_size = 20

        path = ai.astar_search(start, goal, snake, grid_size)
        assert path is not None
        assert path[0] == start
        assert path[:-1] == goal

    def test_astar_search_avoids_snake_body(self):
        ai = SnakeAI(strategy='astar')
        start = (5, 5)
        goal = (5, 10)
        # Snake blocks direct path
        snake = [(5, 5), (5, 6), (5, 7), (5, 8)]
        grid_size = 20

        path = ai.astar_search(start, goal, snake, grid_size)
        if path:
            # Path should go around snake body
            for pos in path[1:]:    # Skip start position
                assert pos not in snake[:-1]    # Exclude tail

    def test_astar_returns_none_when_no_path(self):
        ai = SnakeAI(strategy='astar')
        start_pos = (5, 5)
        goal = (10, 10)
        # Completely surround the start position
        snake = [
            (5, 5),                            # Start
            (4, 5), (6, 5), (5, 4), (5, 6),    # Adjacent
            (4, 4), (6, 4), (4, 6), (6, 6),    # Diagonal
        ]
        grid_size = 20
        path = ai.astar_search(start_pos, goal, snake, grid_size)
        assert path is None

class TestSafetyChecks:
    """
        Test safety checking methods
    """
    def test_is_move_safe_detects_wall_collision(self):
        ai = SnakeAI()
        head = (0, 10)
        direction = Direction.LEFT
        game_state = {
            'snake': [(0, 10), (1, 10)],
            'grid': 20,
        }
        is_safe = ai.is_move_safe(head, direction, game_state)
        assert is_safe is False     # Would hit wall

    def test_is_move_safe_detects_self_collision(self):
        ai = SnakeAI()
        head = (5, 5)
        direction = Direction.DOWN
        game_state = {
            'snake': [(5, 5), (5, 6), (6, 6), (6, 5), (5, 4)],
            'grid_size': 20,
        }
        is_safe = ai.is_move_safe(head, direction, game_state)
        assert is_safe is False     # Would hit own body

    def test_is_move_safe_allows_safe_move(self):
        ai = SnakeAI()
        head = (10, 10)
        direction = Direction.UP
        game_state = {
            'snake': [(10, 10), (10, 11), (10, 12)],
            'grid_size': 20,
        }
        is_safe = ai.is_move_safe(head, direction, game_state)
        assert is_safe is True

    def test_has_escape_route_true_when_routes_exist(self):
        ai = SnakeAI()
        position = (10, 10)
        game_state = {
            'snake': [(9, 10), (9, 11)],  # Away from position
            'grid_size': 20,
        }
        has_route = ai.has_escape_route(position, game_state)
        assert has_route is True

    def test_count_reachable_spaces(self):
        ai = SnakeAI()
        start_pos = (10, 10)
        game_state = {
            'snake': [(5, 5), (5, 6)],  # Far away
            'grid_size': 20,
        }
        count = ai.count_reachable_spaces(start_pos, game_state)
        assert count > 0
        assert count <= 100  # Limited by search depth

class TestUtilityMethods:
    """
        Test utility methods
    """
    def test_get_next_position_up(self):
        ai = SnakeAI()
        pos = ai.get_next_position((5, 5), Direction.UP)
        assert pos == (5, 4)

    def test_get_next_position_down(self):
        ai = SnakeAI()
        pos = ai.get_next_position((5, 5), Direction.DOWN)
        assert pos == (5, 6)

    def test_get_next_position_left(self):
        ai = SnakeAI()
        pos = ai.get_next_position((5, 5), Direction.LEFT)
        assert pos == (4, 5)

    def test_get_next_position_right(self):
        ai = SnakeAI()
        pos = ai.get_next_position((5, 5), Direction.RIGHT)
        assert pos == (6, 5)

    def test_get_direction_to_position_left(self):
        ai = SnakeAI()
        direction = ai.get_direction_to_position((5, 5), (4, 5))
        assert direction == Direction.LEFT

    def test_get_direction_to_position_right(self):
        ai = SnakeAI()
        direction = ai.get_direction_to_position((5, 5), (6, 5))
        assert direction == Direction.RIGHT

    def test_get_direction_to_position_up(self):
        ai = SnakeAI()
        direction = ai.get_direction_to_position((5, 5), (5, 4))
        assert direction == Direction.UP

    def test_get_direction_to_position_down(self):
        ai = SnakeAI()
        direction = ai.get_direction_to_position((5, 5), (5, 6))
        assert direction == Direction.DOWN

class TestDifferentStrategies:
    """
        Compare different AI strategies
    """
    def test_all_strategies_return_valid_direction(self, sample_game_state):
        strategies = ['simple', 'astar', 'safe']
        for strategy_name in strategies:
            ai = SnakeAI(strategy=strategy_name)
            direction = ai.get_next_move(sample_game_state)
            assert isinstance(direction, Direction), f"{strategy_name} failed"

    def test_strategies_handle_tight_spaces(self):
        game_state = {
            'snake': [(2, 2), (2, 3), (3, 3)],
            'food': (18, 18),   # Far away
            'direction': 'up',
            'grid_size': 20,
            'score': 0,
            'game_over': False,
            'moves': 0,
        }
        for strategy in ['simple', 'astar', 'safe']:
            ai = SnakeAI(strategy=strategy)
            direction = ai.get_next_move(game_state)
            assert isinstance(direction, Direction)


# Integration test
def test_ai_plays_complete_game():
    """
        Test AI can play through a short game
    """
    from game.game_engine import SnakeGame

    game = SnakeGame(grid_size=10)
    ai = SnakeAI(strategy='astar')
    max_moves = 50
    moves = 0

    while not game.game_over and moves < max_moves:
        state = game.get_state()
        direction = ai.get_next_move(state)
        game.change_direction(direction)
        game.update()
        moves += 1
    # AI should survive at least a few moves
    assert moves > 5
