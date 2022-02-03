# -----------------------------
#   IMPORTS
# -----------------------------
# Import the necessary packages
from django.db import models

# Create your models here.


# -----------------------------
#   NOTE MODEL CLASS
# -----------------------------
class Note(models.Model):
    body = models.TextField(null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    # -----------------------------
    #   FUNCTIONS
    # -----------------------------
    def __str__(self):
        return self.body[0:50]
