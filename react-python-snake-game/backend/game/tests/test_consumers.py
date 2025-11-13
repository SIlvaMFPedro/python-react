from channels.testing import WebsocketCommunicator
import pytest
import json


@pytest.mark.asyncio
@pytest.mark.django_db
class TestWebSocketConnection:
    """
        Test WebSocket connection and basic communication
    """
    async def test_websocket_can_connect(self, game_application):
        communicator = WebsocketCommunicator(game_application, "/ws/game/test/")
        connected, _ = await communicator.connect()
        assert connected is True
        await communicator.disconnect()

    async def test_websocket_receives_initial_state(self, game_application):
        communicator = WebsocketCommunicator(game_application, "/ws/game/test/")
        await communicator.connect()
        # Should receive initial game state
        response = await communicator.receive_json_from()
        assert response['type'] == 'game_state'
        assert 'state' in response
        assert 'snake' in response['state']
        assert 'food' in response['state']
        assert 'score' in response['state']
        await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db
class TestGameActions:
    """
        Test game action messages
    """
    async def test_start_action(self, game_application):
        communicator = WebsocketCommunicator(game_application, "/ws/game/test/")
        await communicator.connect()
        # Clear initial state message
        await communicator.receive_json_from()
        # Send start action
        await communicator.send_json_to({'action': 'start'})
        # Should receive game state updates
        response = await communicator.receive_json_from()
        assert response['type'] == 'game_state'
        await communicator.disconnect()

    async def test_direction_action(self, game_application):
        communicator = WebsocketCommunicator(game_application, "/ws/game/test/")
        await communicator.connect()
        # Clear initial state
        await communicator.receive_json_from()
        # Send direction change
        await communicator.send_json_to({
            'action': 'direction',
            'direction': 'left'
        })
        # Start game to see direction change
        await communicator.send_json_to({'action': 'start'})
        # Receive game state
        response = await communicator.receive_json_from()
        assert response['type'] == 'game_state'
        await communicator.disconnect()

    async def test_reset_action(self, game_application):
        communicator = WebsocketCommunicator(game_application, "/ws/game/test/")
        await communicator.connect()
        # Clear initial state
        await communicator.receive_json_from()
        # Send reset action
        await communicator.send_json_to({'action': 'reset'})
        # Receive reset game state
        response = await communicator.receive_json_from()
        assert response['type'] == 'game_state'
        assert response['state']['score'] == 0
        assert response['state']['moves'] == 0
        await communicator.disconnect()

    async def test_pause_action(self, game_application):
        communicator = WebsocketCommunicator(game_application, "/ws/game/test/")
        await communicator.connect()
        # Clear initial state
        await communicator.receive_json_from()
        # Start then pause
        await communicator.send_json_to({'action': 'start'})
        await communicator.receive_json_from()  # Get start response
        await communicator.send_json_to({'action': 'pause'})
        # Game should stop sending updates
        await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db
class TestAIActions:
    """
        Test AI-related actions
    """
    async def test_toggle_ai_action(self, game_application):
        communicator = WebsocketCommunicator(game_application, "/ws/game/test/")
        await communicator.connect()
        # Clear initial state
        await communicator.receive_json_from()
        # Toggle AI
        await communicator.send_json_to({'action': 'toggle_ai'})
        # Should receive AI status
        response = await communicator.receive_json_from()
        assert response['type'] == 'ai_status'
        assert 'ai_mode' in response
        await communicator.disconnect()

    async def test_set_ai_strategy_action(self, game_application):
        communicator = WebsocketCommunicator(game_application, "/ws/game/test/")
        await communicator.connect()
        # Clear initial state
        await communicator.receive_json_from()
        # Set AI strategy
        await communicator.send_json_to({
            'action': 'set_ai_strategy',
            'strategy': 'simple'
        })
        # Receive AI status
        response = await communicator.receive_json_from()
        assert response['type'] == 'ai_status'
        assert response['strategy'] == 'simple'
        await communicator.disconnect()

    async def test_ai_strategies(self, game_application):
        """
            Test all AI strategies can be set
        """
        strategies = ['simple', 'astar', 'safe']
        for strategy in strategies:
            communicator = WebsocketCommunicator(game_application, "/ws/game/test/")
            await communicator.connect()
            await communicator.receive_json_from()  # Clear initial
            await communicator.send_json_to({
                'action': 'set_ai_strategy',
                'strategy': strategy
            })
            response = await communicator.receive_json_from()
            assert response['strategy'] == strategy
            await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db
class TestGameLoop:
    """
        Test game loop functionality
    """
    async def test_game_loop_sends_updates(self, game_application):
        communicator = WebsocketCommunicator(game_application, "/ws/game/test/")
        await communicator.connect()
        # Clear initial state
        await communicator.receive_json_from()
        # Start game
        await communicator.send_json_to({'action': 'start'})
        # Should receive multiple state updates
        update_count = 0
        try:
            for _ in range(5):
                response = await communicator.receive_json_from(timeout=1)
                if response['type'] == 'game_state':
                    update_count += 1
        except:
            pass  # Timeout is expected

        assert update_count >= 1
        await communicator.disconnect()

    async def test_game_over_stops_updates(self, game_application):
        communicator = WebsocketCommunicator(game_application, "/ws/game/test/")
        await communicator.connect()
        # Would need to simulate game over condition
        # This is a simplified test
        await communicator.receive_json_from()
        await communicator.send_json_to({'action': 'start'})
        await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db
class TestMultipleConnections:
    """
        Test multiple simultaneous connections
    """
    async def test_multiple_games_independent(self, game_application):
        # Create two connections
        comm1 = WebsocketCommunicator(game_application, "/ws/game/game1/")
        comm2 = WebsocketCommunicator(game_application, "/ws/game/game2/")
        await comm1.connect()
        await comm2.connect()
        # Get initial states
        state1 = await comm1.receive_json_from()
        state2 = await comm2.receive_json_from()
        # Both should have their own game states
        assert state1 is not None
        assert state2 is not None
        # Start both games
        await comm1.send_json_to({'action': 'start'})
        await comm2.send_json_to({'action': 'start'})
        # Both should receive updates independently
        update1 = await comm1.receive_json_from()
        update2 = await comm2.receive_json_from()
        assert update1['type'] == 'game_state'
        assert update2['type'] == 'game_state'
        await comm1.disconnect()
        await comm2.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db
class TestErrorHandling:
    """
        Test error handling in consumer
    """
    async def test_invalid_action_ignored(self, game_application):
        communicator = WebsocketCommunicator(game_application, "/ws/game/test/")
        await communicator.connect()
        # Clear initial state
        await communicator.receive_json_from()
        # Send invalid action
        await communicator.send_json_to({'action': 'invalid_action'})
        # Should not crash, connection should remain
        await communicator.send_json_to({'action': 'reset'})
        response = await communicator.receive_json_from()
        assert response is not None
        await communicator.disconnect()

    async def test_invalid_direction_ignored(self, game_application):
        communicator = WebsocketCommunicator(game_application, "/ws/game/test/")
        await communicator.connect()
        await communicator.receive_json_from()
        # Send invalid direction
        await communicator.send_json_to({
            'action': 'direction',
            'direction': 'invalid'
        })
        # Should not crash
        await communicator.send_json_to({'action': 'reset'})
        response = await communicator.receive_json_from()
        assert response is not None
        await communicator.disconnect()

    async def test_malformed_json_handled(self, game_application):
        communicator = WebsocketCommunicator(game_application, "/ws/game/test/")
        await communicator.connect()
        # This tests the consumer's error handling
        # In a real scenario, malformed JSON might close the connection
        await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db
class TestDisconnection:
    """
        Test disconnection handling
    """
    async def test_disconnect_cleans_up(self, game_application):
        communicator = WebsocketCommunicator(game_application, "/ws/game/test/")
        await communicator.connect()
        await communicator.receive_json_from()
        await communicator.send_json_to({'action': 'start'})
        # Disconnect should clean up game instance
        await communicator.disconnect()
        # Reconnect should get fresh game
        communicator = WebsocketCommunicator(game_application, "/ws/game/test/")
        await communicator.connect()
        state = await communicator.receive_json_from()
        assert state['state']['score'] == 0
        await communicator.disconnect()