# -----------------------------
#   IMPORTS
# -----------------------------
# Import the necessary packages
from django.db import models

# Create your models here.


# -----------------------------
#   REACT CLASS MODEL
# -----------------------------
class React(models.Model):
    employee = models.CharField(max_length=30)
    department = models.CharField(max_length=200)