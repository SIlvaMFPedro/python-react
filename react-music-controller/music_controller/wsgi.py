# -----------------------------
#   IMPORTS
# -----------------------------
# Import the necessary packages
from django.core.wsgi import get_wsgi_application
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'music_controller.settings')

application = get_wsgi_application()
