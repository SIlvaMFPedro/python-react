from time import sleep

from channels.generic.websocket import AsyncWebsocketConsumer
from .game_engine import SnakeGame, Direction
import json
import asyncio

class GameConsumer(AsyncWebsocketConsumer):
    # Store game instances per connection
    games = {}

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.is_running = None
        self.game_loop_task = None
        self.game_channel = None
        self.game_id = None

    async def connect(self):
        """
            Create client connection
        """
        await self.accept()

        # Create a new game instance for this connection
        self.game_id = self.scope['url_route']['kwargs'].get('game_id', 'default')
        self.games[self.game_channel] = SnakeGame(grid_size=20)
        self.game_loop_task = None
        self.is_running = False

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

        # Clean up game instance
        if self.channel_name in self.games:
            del self.games[self.channel_name]

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
            # Change direction
            direction_str = data.get('direction')
            try:
                direction = Direction(direction_str)
                game.change_direction(direction)
            except ValueError:
                pass

        elif action == 'reset':
            # Reset game
            game.reset()
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

    async def game_loop(self):
        """
            Main game loop that updates and sends state
        """
        game = self.games.get(self.channel_name)

        try:
            while self.is_running and game and not game.game_over:
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
                'state': game.get_state()
            }))

