from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # Blackjack game websocket
    re_path(r'ws/blackjack/(?P<game_id>\w+)/$', consumers.BlackJackConsumer.as_asgi()),
]