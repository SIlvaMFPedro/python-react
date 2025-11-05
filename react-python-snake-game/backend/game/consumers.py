from time import sleep

from channels.generic.websocket import AsyncWebsocketConsumer
from game_engine import SnakeGame, Direction
from ai_agent import SnakeAI
import json
import asyncio

class GameConsumer(AsyncWebsocketConsumer):
    # Store game instances per connection
    games = {}
    # Store AI agents per connection
    ai_agents = {}

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.ai_strategy = None
        self.ai_mode = None
        self.is_running = None
        self.game_loop_task = None
        self.channel_name = None
        self.game_id = None

    async def connect(self):
        """
            Create client connection
        """
        await self.accept()

        # Create a new game instance for this connection
        self.game_id = self.scope['url_route']['kwargs'].get('game_id', 'default')
        self.games[self.channel_name] = SnakeGame(grid_size=20)
        self.ai_agents[self.channel_name] = SnakeAI(strategy='astar')
        self.game_loop_task = None
        self.is_running = False
        self.ai_mode = False
        self.ai_strategy = 'astar'

        # Send initial game state
        await self.send_game_state()

    async def disconnect(self, close_code):
        """
            Close client connection
        """
        # Stop game loop
        if self.game_loop_task:
            self.is_running = False
            self.game_loop_task.cancel()

        # Clean up game instance and AI agents
        if self.channel_name in self.games:
            del self.games[self.channel_name]
        if self.channel_name in self.ai_agents:
            del self.ai_agents[self.channel_name]

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')

        game = self.games.get(self.channel_name)
        if not game:
            return

        if action == 'start':
            # Start game loop
            if not self.is_running:
                self.is_running = True
                self.game_loop_task = asyncio.create_task(self.game_loop())

        elif action == 'direction':
            # Change direction (only if not in AI mode)
            if not self.ai_mode:
                direction_str = data.get('direction')
                try:
                    direction = Direction(direction_str)
                    game.change_direction(direction)
                except ValueError:
                    pass

        elif action == 'reset':
            # Reset game
            game.reset()
            self.ai_mode = False
            if self.game_loop_task:
                self.is_running = False
                self.game_loop_task.cancel()
            await self.send_game_state()

        elif action == 'pause':
            # Pause game
            if self.is_running:
                self.is_running = False
                if self.game_loop_task:
                    self.game_loop_task.cancel()

        elif action == 'toggle_ai':
            # Toggle AI mode
            self.ai_mode = not self.ai_mode
            await self.send(text_data=json.dumps({
                'type': 'ai_status',
                'ai_mode': self.ai_mode,
                'strategy': self.ai_strategy
            }))

        elif action == 'set_ai_strategy':
            # Change AI strategy
            strategy = data.get('strategy', 'astar')
            if strategy in ['simple', 'astar', 'safe']:
                self.ai_strategy = strategy
                self.ai_agents[self.channel_name] = SnakeAI(strategy=strategy)
                await self.send(text_data=json.dumps({
                    'type': 'ai_status',
                    'ai_mode': self.ai_mode,
                    'strategy': self.ai_strategy
                }))

    async def game_loop(self):
        """
            Main game loop that updates and sends state
        """
        game = self.games.get(self.channel_name)
        ai_agent = self.ai_agents.get(self.channel_name)

        try:
            while self.is_running and game and not game.game_over:
                # If AI mode is enabled, let AI decide direction
                if self.ai_mode and ai_agent:
                    game_state = game.get_state()
                    next_direction = ai_agent.get_next_move(game_state)
                    game.change_direction(next_direction)
                game.update()
                await self.send_game_state()
                await asyncio.sleep(0.15)     # wait for 150ms

            # Send final state if game is over
            if game and game.game_over:
                await self.send_game_state()
                self.is_running = False

        except asyncio.CancelledError:
            pass

    async def send_game_state(self):
        """
            Send current game state to client
        """
        game = self.games.get(self.channel_name)
        if game:
            await self.send(text_data=json.dumps({
                'type': 'game_state',
                'state': game.get_state(),
                'ai_mode': self.ai_mode,
                'ai_strategy': self.ai_strategy
            }))

