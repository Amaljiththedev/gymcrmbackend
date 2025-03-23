from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Expense
from .serializers import ExpenseSerializer

class ExpenseViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for managing expenses.
    Supports filtering by category, date range, trainer, and staff.
    """
    queryset = Expense.objects.all().order_by("-created_at")  # Latest expenses first
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]  # Only authenticated users can access
    
    # Filtering & searching
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["category", "trainer", "staff"]
    search_fields = ["description"]
    ordering_fields = ["amount", "created_at"]