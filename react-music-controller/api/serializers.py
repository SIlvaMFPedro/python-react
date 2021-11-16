# -----------------------------
#   IMPORTS
# -----------------------------
# Import the necessary packages
from rest_framework import serializers
from .models import Room


# ------------------------------
#  ROOM MODEL SERIALIZER CLASS
# ------------------------------
class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = {'id', 'code', 'host', 'guest_can_pause', 'votes_to_skip', 'created_at'}
