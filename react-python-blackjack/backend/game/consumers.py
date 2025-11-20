from channels.generic.websocket import AsyncWebsocketConsumer
from .game_engine import BlackJackGame
import json

class BlackJackConsumer(AsyncWebsocketConsumer):
    games = {}      # store game instances per connection here

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.game_id = None

    async def connect(self):
        await self.accept()
        # Create new game instance for this connection
        self.game_id = self.scope['url_route']['kwargs'].get('game_id', 'default')
        self.games[self.channel_name] = BlackJackGame(num_decks=6)
        # Send initial game state
        await self.send_game_state()

    async def disconnect(self, close_code):
        # Clean up game instance
        if self.channel_name in self.games:
            del self.games[self.channel_name]

    async def receive(self, text_data):
        """
            Receive game data from the client
        """
        try:
            data = json.loads(text_data)
            action = data.get('action')
            game = self.games.get(self.channel_name)
            if not game:
                await self.send_error("Game not found!")
                return
            # Handle different actions
            if action == "bet":
                amount = data.get('amount', 0)
                if game.place_bet(amount):
                    await self.send_game_state()
                else:
                    await self.send_error("Invalid bet amount!")
            elif action == "deal":
                if game.start_round():
                    await self.send_game_state()
                else:
                    await self.send_error("Cannot deal - place bet first!")
            elif action == "hit":
                if game.hit():
                    await self.send_game_state()
                else:
                    await self.send_error("Cannot hit now!")
            elif action == "stand":
                if game.stand():
                    await self.send_game_state()
                else:
                    await self.send_error("Cannot stand now!")
            elif action == "double":
                if game.double_down():
                    await self.send_game_state()
                else:
                    await self.send_error("Cannot double down - Insufficient chips or invalid hand!")
            elif action == "split":
                if game.split():
                    await self.send_game_state()
                else:
                    await self.send_error("Cannot split - Insufficient chips or invalid hand!")
            elif action == "surrender":
                if game.surrender():
                    await self.send_game_state()
                else:
                    await self.send_error("Cannot surrender now!")
            elif action == "insurance":
                if game.buy_insurance():
                    await self.send_game_state()
                else:
                    await self.send_error("Cannot buy insurance - Insufficient chips or dealer doesn't show Ace!")
            elif action == "reset":
                game.reset_round()
                await self.send_game_state()
            else:
                await self.send_error(f"Unknown action: {action}")
        except Exception as e:
            await self.send_error(f"Error processing action: {str(e)}")

    async def send_game_state(self):
        """
            Send current game state to the client
        """
        game = self.games.get(self.channel_name)
        if game:
            # Hide dealer's first card during play
            hide_dealer_card = game.game_phase in ['betting', 'playing']
            # Send game state message
            await self.send(text_data=json.dumps({
                'type': 'game_state',
                'state': game.get_state(hide_dealer_card=hide_dealer_card)
            }))

    async def send_error(self, error_message: str):
        """
            Sends error message to the client
        """
        # Send error message
        await self.send(text_data=json.dumps({
            'type': 'error',
            'error': error_message
        }))

    async def send_info(self, info_message: str):
        """
            Sends info message to the client
        """
        # Send info message
        await self.send(text_data=json.dumps({
            'type': 'info',
            'message': info_message
        }))