# -----------------------------
#   IMPORTS
# -----------------------------
# Import the necessary packages
from django.apps import AppConfig


# -----------------------------
#  API CONFIGURATION CLASS
# -----------------------------
class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
