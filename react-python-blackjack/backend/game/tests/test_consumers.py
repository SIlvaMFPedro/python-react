from channels.testing import WebsocketCommunicator
from channels.routing import URLRouter
from django.db.transaction import commit
from django.urls import re_path
from game.consumers import BlackJackConsumer
import json
import pytest
import asyncio

@pytest.fixture
def blackjack_application():
    """Create test application for Blackjack WebSocket"""
    return URLRouter([
        re_path(r'ws/blackjack/(?P<game_id>\w+)/$', BlackJackConsumer.as_asgi()),
    ])


@pytest.mark.asyncio
@pytest.mark.django_db
class TestBlackjackWebSocketConnection:
    """
        Test WebSocket connection
    """
    async def test_can_connect(self, blackjack_application):
        communicator = WebsocketCommunicator(blackjack_application, "/ws/blackjack/test/")
        connected, _ = await communicator.connect()
        assert connected is True
        await communicator.disconnect()

    async def test_receives_initial_state(self, blackjack_application):
        communicator = WebsocketCommunicator(blackjack_application, "/ws/blackjack/test/")
        await communicator.connect()
        response = await communicator.receive_json_from()
        assert response['type'] == 'game_state'
        assert 'state' in response
        assert response['state']['player_chips'] == 1000
        assert response['state']['game_phase'] == 'betting'
        await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db
class TestBettingActions:
    """
        Test betting phase actions
    """
    async def test_place_bet(self, blackjack_application):
        communicator = WebsocketCommunicator(blackjack_application, "/ws/blackjack/test/")
        await communicator.connect()
        await communicator.receive_json_from()  # Initial state
        # Place bet
        await communicator.send_json_to({'action': 'bet', 'amount': 100})
        response = await communicator.receive_json_from()
        assert response['type'] == 'game_state'
        assert response['state']['current_bet'] == 100
        assert response['state']['player_chips'] == 900
        await communicator.disconnect()

    async def test_place_invalid_bet(self, blackjack_application):
        communicator = WebsocketCommunicator(blackjack_application, "/ws/blackjack/test/")
        await communicator.connect()
        await communicator.receive_json_from()
        # Try invalid bet
        await communicator.send_json_to({'action': 'bet', 'amount': 5000})
        response = await communicator.receive_json_from()
        assert response['type'] == 'error'
        await communicator.disconnect()

    async def test_deal_cards(self, blackjack_application):
        communicator = WebsocketCommunicator(blackjack_application, "/ws/blackjack/test/")
        await communicator.connect()
        await communicator.receive_json_from()
        # Place bet and deal
        await communicator.send_json_to({'action': 'bet', 'amount': 100})
        await communicator.receive_json_from()
        await communicator.send_json_to({'action': 'deal'})
        response = await communicator.receive_json_from()
        assert response['type'] == 'game_state'
        assert response['state']['game_phase'] == 'playing'
        assert len(response['state']['player_hands']) == 1
        assert len(response['state']['player_hands'][0]['cards']) == 2
        assert len(response['state']['dealer_hand']['cards']) == 2
        await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db
class TestPlayingActions:
    """
        Test playing phase actions
    """
    async def setup_game(self, communicator):
        """
            Helper to set up a game in playing state
        """
        await communicator.connect()
        await communicator.receive_json_from()  # Initial
        await communicator.send_json_to({'action': 'bet', 'amount': 100})
        await communicator.receive_json_from()  # Bet response
        await communicator.send_json_to({'action': 'deal'})
        await communicator.receive_json_from()  # Deal response

    async def test_hit_action(self, blackjack_application):
        communicator = WebsocketCommunicator(blackjack_application, "/ws/blackjack/test/")
        await self.setup_game(communicator)
        # Hit
        await communicator.send_json_to({'action': 'hit'})
        response = await communicator.receive_json_from()
        assert response['type'] == 'game_state'
        assert len(response['state']['player_hands'][0]['cards']) >= 3
        await communicator.disconnect()

    async def test_stand_action(self, blackjack_application):
        communicator = WebsocketCommunicator(blackjack_application, "/ws/blackjack/test/")
        await self.setup_game(communicator)
        # Stand
        await communicator.send_json_to({'action': 'stand'})
        response = await communicator.receive_json_from()
        assert response['type'] == 'game_state'
        assert response['state']['game_phase'] == 'finished'
        await communicator.disconnect()

    async def test_double_action(self, blackjack_application):
        communicator = WebsocketCommunicator(blackjack_application, "/ws/blackjack/test/")
        await self.setup_game(communicator)
        # Double down
        await communicator.send_json_to({'action': 'double'})
        response = await communicator.receive_json_from()
        # Should work or fail gracefully
        assert response['type'] in ['game_state', 'error']
        await communicator.disconnect()

    async def test_reset_action(self, blackjack_application):
        communicator = WebsocketCommunicator(blackjack_application, "/ws/blackjack/test/")
        await self.setup_game(communicator)
        # Reset
        await communicator.send_json_to({'action': 'reset'})
        response = await communicator.receive_json_from()
        assert response['type'] == 'game_state'
        assert response['state']['game_phase'] == 'betting'
        assert response['state']['current_bet'] == 0
        await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db
class TestAIActions:
    """
        Test AI-related actions
    """
    async def test_toggle_ai(self, blackjack_application):
        communicator = WebsocketCommunicator(blackjack_application, "/ws/blackjack/test/")
        await communicator.connect()
        await communicator.receive_json_from()
        # Toggle AI
        await communicator.send_json_to({'action': 'toggle_ai'})
        response = await communicator.receive_json_from()
        assert response['type'] == 'ai_status'
        assert 'ai_mode' in response
        await communicator.disconnect()

    async def test_set_ai_strategy(self, blackjack_application):
        communicator = WebsocketCommunicator(blackjack_application, "/ws/blackjack/test/")
        await communicator.connect()
        await communicator.receive_json_from()
        # Set AI strategy
        await communicator.send_json_to({'action': 'set_ai_strategy', 'strategy': 'simple'})
        response = await communicator.receive_json_from()
        assert response['type'] == 'ai_status'
        assert response['strategy'] == 'simple'
        await communicator.disconnect()

    async def test_ai_makes_bet_automatically(self, blackjack_application):
        communicator = WebsocketCommunicator(blackjack_application, "/ws/blackjack/test/")
        await communicator.connect()
        await communicator.receive_json_from()
        # Toggle AI on
        await communicator.send_json_to({'action': 'toggle_ai'})
        await communicator.receive_json_from()  # AI status
        # AI should make a bet automatically
        # Wait for AI to place bet
        await asyncio.sleep(1)
        # Should receive game state updates
        response = await communicator.receive_json_from(timeout=2)
        assert response['type'] in ['game_state', 'info']
        await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db
class TestErrorHandling:
    """
        Test error handling
    """
    async def test_invalid_action(self, blackjack_application):
        communicator = WebsocketCommunicator(blackjack_application, "/ws/blackjack/test/")
        await communicator.connect()
        await communicator.receive_json_from()
        # Send invalid action
        await communicator.send_json_to({'action': 'invalid_action'})
        response = await communicator.receive_json_from()
        assert response['type'] == 'error'
        await communicator.disconnect()

    async def test_hit_when_not_playing(self, blackjack_application):
        communicator = WebsocketCommunicator(blackjack_application, "/ws/blackjack/test/")
        await communicator.connect()
        await communicator.receive_json_from()
        # Try to hit in betting phase
        await communicator.send_json_to({'action': 'hit'})
        response = await communicator.receive_json_from()
        assert response['type'] == 'error'
        await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db
class TestMultipleConnections:
    """
        Test multiple simultaneous games
    """
    async def test_independent_games(self, blackjack_application):
        # Create two connections
        comm1 = WebsocketCommunicator(blackjack_application, "/ws/blackjack/game1/")
        comm2 = WebsocketCommunicator(blackjack_application, "/ws/blackjack/game2/")
        await comm1.connect()
        await comm2.connect()
        # Get initial states
        state1 = await comm1.receive_json_from()
        state2 = await comm2.receive_json_from()
        assert state1 is not None
        assert state2 is not None
        # Place different bets
        await comm1.send_json_to({'action': 'bet', 'amount': 100})
        await comm2.send_json_to({'action': 'bet', 'amount': 200})
        response1 = await comm1.receive_json_from()
        response2 = await comm2.receive_json_from()
        assert response1['state']['current_bet'] == 100
        assert response2['state']['current_bet'] == 200
        await comm1.disconnect()
        await comm2.disconnect()

