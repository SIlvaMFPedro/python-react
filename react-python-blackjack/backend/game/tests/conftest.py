from pathlib import Path
from channels.testing import WebsocketCommunicator
import django
import sys
import os
import pytest

# Add the project root to Python path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

# Setup Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# Configure Django before importing models
django.setup()

@pytest.fixture(scope='session')
def django_db_setup():
    """
        Setup test database
    """
    pass

@pytest.fixture
def sample_game_state():
    """
        Fixture providing a sample game state for AI tests
    """

@pytest.fixture
def game_application():
    """
        Create a test application for Websocket testing
    """
    from channels.routing import URLRouter
    from django.urls import re_path
    from game.consumers import BlackJackConsumer

    return URLRouter([
        re_path(r'ws/blackjack/(?P<game_id>\w+)/$', BlackJackConsumer.as_asgi())
    ])

# Pytest configuration hooks
def pytest_configure(config):
    """
        Configure pytest with Django settings
    """
    from django.conf import settings
    # Ensure test mode settings
    settings.DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }
    settings.CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels.layers.InMemoryChannelLayer'
        }
    }
