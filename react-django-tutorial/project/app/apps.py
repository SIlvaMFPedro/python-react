# -----------------------------
#   IMPORTS
# -----------------------------
# Import the necessary packages
from django.apps import AppConfig


# -----------------------------
#   APP CONFIGURATION CLASS
# -----------------------------
class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'
