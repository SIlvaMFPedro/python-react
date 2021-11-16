# -----------------------------
#   IMPORTS
# -----------------------------
# Import the necessary packages
from django.shortcuts import render
from rest_framework import generics
from .serializers import RoomSerializer
from .models import Room

# Create your views here


# -----------------------------
#   ROOM VIEW CLASS
# -----------------------------
class RoomView(generics.ListAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer