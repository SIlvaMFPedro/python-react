"""
WSGI config for notepad project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""
# -----------------------------
#   IMPORTS
# -----------------------------
# Import the necessary packages
import os
from django.core.wsgi import get_wsgi_application

# Set the default environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'notepad.settings')

# Get the WSGI application
application = get_wsgi_application()
