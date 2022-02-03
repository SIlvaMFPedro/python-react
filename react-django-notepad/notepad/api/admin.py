# -----------------------------
#   IMPORTS
# -----------------------------
# Import the necessary packages
from django.contrib import admin
from .models import Note

# Register your models here.
admin.site.register(Note)
