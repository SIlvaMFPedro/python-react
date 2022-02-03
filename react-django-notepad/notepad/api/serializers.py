# -----------------------------
#   IMPORTS
# -----------------------------
# Import the necessary packages
from rest_framework.serializers import ModelSerializer
from .models import Note


# -----------------------------
#   NOTE MODEL SERIALIZER
# -----------------------------
class NoteSerializer(ModelSerializer):
    class Meta:
        model = Note
        fields = '__all__'
