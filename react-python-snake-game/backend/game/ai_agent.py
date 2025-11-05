from collections import deque
import heapq
from .game_engine import Direction

class SnakeAI:
    """
        AI Agent for Snake game with multiple strategies
    """

    def __init__(self, strategy='astar'):
        """
            Initialize AI with a strategy ('simple', 'astar' or 'safe')
        """
        self.strategy = strategy

    def get_next_move(self, game_state):
        """
            Determine the next move based on the current game state
            Returns: Direction enum
        """
        if self.strategy == 'simple':
            return self.simple_strategy(game_state)
        elif self.strategy == 'astar':
            return self.astar_strategy(game_state)
        elif self.strategy == 'safe':
            return self.safe_strategy(game_state)
        else:
            return self.simple_strategy(game_state)

    def simple_strategy(self, game_state):
        """
            Simple greedy approach: move towards the food
        """
        snake = game_state['snake']
        food = game_state['food']
        head = snake[0]
        current_direction = Direction(game_state['direction'])

        head_x, head_y = head
        food_x, food_y = food

        # Calculate direction to food
        dx = food_x - head_x
        dy = food_y - head_y

        # Prioritize the axis with larger distance
        possible_moves = []

        if abs(dx) > abs(dy):
            if dx > 0:
                possible_moves.append(Direction.RIGHT)
            elif dx < 0:
                possible_moves.append(Direction.LEFT)
            if dy > 0:
                possible_moves.append(Direction.DOWN)
            elif dy < 0:
                possible_moves.append(Direction.UP)
        else:
            if dy > 0:
                possible_moves.append(Direction.DOWN)
            elif dy < 0:
                possible_moves.append(Direction.UP)
            if dx > 0:
                possible_moves.append(Direction.RIGHT)
            elif dx < 0:
                possible_moves.append(Direction.LEFT)

        # Try moves in order, checking for safety
        for move in possible_moves:
            if self.is_move_safe(head, move, game_state):
                return move

        # If no safe move towards food, try and safe move
        for direction in Direction:
            if self.is_move_safe(head, direction, game_state):
                return direction

        # No safe move available, return current direction
        return current_direction


    def astar_strategy(self, game_state):
        """
            A* pathfinding algorithm to find optimal path to food
        """
        snake = game_state['snake']
        food = game_state['food']
        head = snake[0]
        grid_size = game_state['grid_size']

        path = self.astar_search(head, food, snake, grid_size)

        if path and len(path) > 1:
            next_pos = path[1]
            direction = self.get_direction_to_position(head, next_pos)
            return direction

        # Fallback to simple strategy if no path found
        return self.simple_strategy(game_state)

    def safe_strategy(self, game_state):
        """
            Safety first strategy: prioritize survival over food
        """

    def astar_search(self, start, goal, snake, grid_size):
        """
            A* pathfinding implementation
            Returns a list of positions from start to goal
        """
        def heuristic(pos):
            return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])

        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: heuristic(start)}

        snake_set = set(snake[:-1]) # Exclude tail as it will move

        while open_set:
            current = heapq.heappop(open_set)[1]
            if current == goal:
                # Reconstruct path
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                return list(reversed(path))

            x, y = current
            neighbors = [
                (x, y - 1),     # UP
                (x, y + 1),     # DOWN
                (x - 1, y),     # LEFT
                (x + 1, y),     # RIGHT
            ]

            for neighbor in neighbors:
                nx, ny = neighbor
                # Check bounds
                if nx < 0 or nx >=grid_size or ny < 0 or ny >= grid_size:
                    continue
                # Check collision
                if neighbor in snake_set:
                    continue

                tentative_g_score = g_score[current] + 1
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + heuristic(neighbor)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

        return None     # No path found


    def is_move_safe(self, head, direction, game_state):
        """
            Check if a move in given direction is safe
        """
        next_pos = self.get_next_position(head, direction)
        snake = game_state['snake']
        grid_size = game_state['grid_size']
        x, y = next_pos

        # Check bounds
        if x < 0 or x >= grid_size or y < 0 or y >= grid_size:
            return False
        # Check collision with snake (excluding the tail which will move obviously)
        if next_pos in snake[:-1]:
            return False
        return True

    def has_escape_route(self, position, game_state):
        """
            Check if position has at least one escape route
        """
        count = 0
        for direction in Direction:
            if self.is_move_safe(position, direction, game_state):
                count += 1
        return count > 0

    def count_reachable_spaces(self, start, game_state):
        """
            Count number of spaces reachable from start position using BFS
        """
        snake = game_state['snake']
        grid_size = game_state['grid_size']
        snake_set = set(snake[:-1])

        visited = {start}
        queue = deque([start])
        count = 0

        while queue and count < 100:        # Limit search depth
            x, y = queue.popleft()
            count += 1
            neighbors = [(x, y-1), (x, y+1), (x-1, y), (x+1, y)]

            for nx, ny in neighbors:
                # Check if it is a new position
                if (nx, ny) in visited:
                    continue
                # Check bounds
                if nx < 0 or nx >= grid_size or ny < 0 or ny >= grid_size:
                    continue
                # Check collision
                if (nx, ny) in snake_set:
                    continue
                visited.add((nx, ny))
                queue.append((nx, ny))

        return count

    def get_next_position(self, position, direction):
        """
            Calculate next position based on direction
        """
        x, y = position

        if direction == Direction.UP:
            return x, y - 1
        elif direction == Direction.DOWN:
            return x, y + 1
        elif direction == Direction.LEFT:
            return x - 1, y
        elif direction == Direction.RIGHT:
            return x + 1, y
        return position

    def get_direction_to_position(self, current, target):
        """
            Determine direction from current position to target
        """
        cx, cy = current
        tx, ty = target

        if tx < cx:
            return Direction.LEFT
        elif tx > cx:
            return Direction.RIGHT
        elif ty < cy:
            return Direction.UP
        elif ty > cy:
            return Direction.DOWN
        else:
            return Direction.UP     # Set UP as default

