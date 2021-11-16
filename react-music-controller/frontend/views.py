# -----------------------------
#   IMPORTS
# -----------------------------
# Import the necessary packages
from django.shortcuts import render

# Create your views here


# -----------------------------
#   FUNCTION
# -----------------------------
def index(request, *args, **kwargs):
    return render(request, 'frontend/index.html')