# -----------------------------
#   IMPORTS
# -----------------------------
# Import the necessary packages
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import *
from .serializer import *

# Create your views here.


# -----------------------------
#   REACT VIEW CLASS
# -----------------------------
class ReactView(APIView):
    # -----------------------------
    #   FUNCTIONS
    # -----------------------------
    def get(self, request):
        output = [{"employee": output.employee, "department": output.department} for output in React.objects.all()]
        return Response(output)

    def post(self, request):
        serializer = ReactSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
