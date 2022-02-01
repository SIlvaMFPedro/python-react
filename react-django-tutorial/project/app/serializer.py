# -----------------------------
#   IMPORTS
# -----------------------------
# Import the necessary packages
from rest_framework import serializers
from .models import *


# -----------------------------
#   REACT SERIALIZER CLASS
# -----------------------------
class ReactSerializer(serializers.ModelSerializer):
    class Meta:
        model = React
        fields = ['employee', 'department']
