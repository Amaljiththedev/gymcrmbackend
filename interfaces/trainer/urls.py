from django.urls import path, include
from rest_framework.routers import DefaultRouter
\
from .views import TrainerViewSet, TrainerDetailView, TrainerListView, TrainerPaymentHistoryViewSet, generate_trainer_payment_history

router = DefaultRouter()
router.register(r'trainers', TrainerViewSet)
router.register(r'trainer-payment-history', TrainerPaymentHistoryViewSet)

urlpatterns = [
    path('trainer/<int:pk>/', TrainerDetailView.as_view(), name='trainer-detail'),
    path('trainers-list/', TrainerListView.as_view(), name='trainer-list'),
    path('trainers-slip/<int:history_id>/', generate_trainer_payment_history, name='generate-salary-slip'),
    path('', include(router.urls)),  # Register all viewset routes automatically
]
