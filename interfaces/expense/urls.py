from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExpenseViewSet, expense_meta, export_expenses

router = DefaultRouter()
router.register(r"expenses", ExpenseViewSet, basename="expense")


urlpatterns = [
    path("", include(router.urls)),
    path("expensesources/", expense_meta, name="expense-meta"),
    path("export/", export_expenses, name="export-expenses"),
]