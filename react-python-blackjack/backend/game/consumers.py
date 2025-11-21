from channels.generic.websocket import AsyncWebsocketConsumer
from .game_engine import BlackJackGame
from .ai_agent import BlackJackAI
import asyncio
import json

class BlackJackConsumer(AsyncWebsocketConsumer):
    games = {}      # store game instances per connection here
    ai_agents = {}  # store AI agents per connection

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.ai_task = None
        self.ai_strategy = None
        self.ai_mode = None
        self.game_id = None

    async def connect(self):
        await self.accept()
        # Create new game instance for this connection
        self.game_id = self.scope['url_route']['kwargs'].get('game_id', 'default')
        self.games[self.channel_name] = BlackJackGame(num_decks=6)
        self.ai_agents[self.channel_name] = BlackJackAI(strategy='basic')
        self.ai_mode = False
        self.ai_strategy = 'basic'
        self.ai_task = None
        # Send initial game state
        await self.send_game_state()

    async def disconnect(self, close_code):
        # Stop AI task if running
        if self.ai_task:
            self.ai_task.cancel()
        # Clean up game instance and AI agents
        if self.channel_name in self.games:
            del self.games[self.channel_name]
        if self.channel_name in self.ai_agents:
            del self.ai_agents[self.channel_name]

    async def receive(self, text_data):
        """
            Receive game data from the client
        """
        try:
            data = json.loads(text_data)
            action = data.get('action')
            game = self.games.get(self.channel_name)
            ai = self.ai_agents.get(self.channel_name)
            if not game:
                await self.send_error("Game not found!")
                return
            # Handle AI toggle
            if action == 'toggle_ai':
                self.ai_mode = not self.ai_mode
                await self.send_ai_status()
                # If AI just enabled and in betting phase, make AI bet
                if self.ai_mode and game.game_phase == 'betting':
                    await asyncio.sleep(0.5)
                    await self.ai_make_bet()
                return
            # Handle AI strategy change
            elif action == 'set_ai_strategy':
                strategy = data.get('strategy', 'basic')
                if strategy in ['simple', 'basic', 'conservative']:
                    self.ai_strategy = strategy
                    self.ai_agents[self.channel_name] = BlackJackAI(strategy=strategy)
                    await self.send_ai_status()
                return
            # If AI mode is on, ignore manual actions during play
            if self.ai_mode and action not in ['reset', 'toggle_ai', 'set_ai_strategy']:
                if game.game_phase == 'playing':
                    await self.send_error("AI is active - disable AI to play manually")
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
                    # If AI mode is on, start AI play
                    if self.ai_mode:
                        self.ai_task = asyncio.create_task(self.ai_play_hand())
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
                if self.ai_task:
                    self.ai_task.cancel()
                await self.send_game_state()
                # If AI mode is enabled make bet for next round
                if self.ai_mode:
                    await asyncio.sleep(0.5)
                    await self.ai_make_bet()
            else:
                await self.send_error(f"Unknown action: {action}")
        except Exception as e:
            await self.send_error(f"Error processing action: {str(e)}")

    async def ai_make_bet(self):
        """
            AI makes a bet decision
        """
        game = self.games.get(self.channel_name)
        ai = self.ai_agents.get(self.channel_name)

        if not game or not ai or game.game_phase != 'betting':
            return

        # Determine bet size based on employed strategy
        base_bet = 25   # Base bet amount
        bet_amount = ai.get_bet_size(base_bet, game.player_chips)
        if game.place_bet(bet_amount):
            await self.send_game_state()
            await self.send_info(f"AI bet ${bet_amount}")
            # Auto-deal after betting
            await asyncio.sleep(1)
            if game.start_round():
                await self.send_game_state()
                await asyncio.sleep(0.5)
                # Start AI play
                self.ai_task = asyncio.create_task(self.ai_play_hand())

    async def ai_play_hand(self):
        """
            AI plays its hand automatically
        """
        game = self.games.get(self.channel_name)
        ai = self.ai_agents.get(self.channel_name)
        if not game or not ai:
            return

        try:
            while game.game_phase == 'playing':
                current_hand = game.player_hands[game.current_hand_index]
                dealer_up_card = game.dealer_hand.cards[0]
                # Check if AI should buy insurance
                if (game.current_hand_index == 0 and
                        dealer_up_card.rank.value == 'A' and not current_hand.is_insured and
                        game.player_chips >= game.current_bet // 2):
                    if ai.should_buy_insurance(dealer_up_card, current_hand):
                        await asyncio.sleep(1)
                        if game.buy_insurance():
                            await self.send_game_state()
                            await self.send_info("AI bought insurance")
                # Get AI's decision
                action = ai.get_action(
                    current_hand,
                    dealer_up_card,
                    can_double=current_hand.can_double(),
                    can_split=current_hand.can_split(),
                    can_surrender=(game.current_hand_index == 0 and len(current_hand.cards) == 2)
                )
                # Delay for visualization
                await asyncio.sleep(1)
                # Execute action
                if action == 'hit':
                    if game.hit():
                        await self.send_game_state()
                        await self.send_info("AI hits")
                    else:
                        break
                elif action == 'stand':
                    if game.stand():
                        await self.send_game_state()
                        await self.send_info("AI stands")
                    else:
                        break
                elif action == 'double':
                    if game.double_down():
                        await self.send_game_state()
                        await self.send_info("AI doubles down")
                    else:
                        # Fallback to hit
                        if game.hit():
                            await self.send_game_state()
                            await self.send_info("AI hits (couldn't double down)")
                        else:
                            break
                elif action == 'split':
                    if game.split():
                        await self.send_game_state()
                        await self.send_info("AI splits")
                    else:
                        # Fallback to hit
                        if game.hit():
                            await self.send_game_state()
                            await self.send_info("AI hits (couldn't split)")
                        else:
                            break
                elif action == 'surrender':
                    if game.surrender():
                        await self.send_game_state()
                        await self.send_info("AI surrenders")
                    else:
                        # Fallback to stand
                        if game.stand():
                            await self.send_game_state()
                            await self.send_info("AI stands (couldn't surrender)")
                        else:
                            break
                else:
                    break

                # Check if game moved to next phase
                if game.game_phase != 'playing':
                    break
            # After game finishes, auto-reset for next round if AI mode is on
            if game.game_phase == 'finished':
                await asyncio.sleep(3)
                game.reset_round()
                await self.send_game_state()
                await asyncio.sleep(1)
                # Make bet for next round
                if self.ai_mode:
                    await self.ai_make_bet()

        except asyncio.CancelledError:
            pass

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
                'state': game.get_state(hide_dealer_card=hide_dealer_card),
                'ai_mode': self.ai_mode,
                'ai_strategy': self.ai_strategy
            }))

    async def send_ai_status(self):
        """
            Send AI status update
        """
        ai = self.ai_agents.get(self.channel_name)
        await self.send(text_data=json.dumps({
            'type': 'ai_status',
            'ai_mode': self.ai_mode,
            'strategy': self.ai_strategy,
            'description': ai.get_strategy_description() if ai else ""
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