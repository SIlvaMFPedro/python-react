"""
ASGI config for notepad project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

# -----------------------------
#   IMPORTS
# -----------------------------
# Import the necessary packages
import os

from django.core.asgi import get_asgi_application

# Set the default environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'notepad.settings')

# Get ASGI application
application = get_asgi_application()
