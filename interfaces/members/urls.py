from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MemberViewSet, MembershipPlanViewSet

router = DefaultRouter()
router.register(r'members', MemberViewSet, basename='member')
router.register(r'membership-plans', MembershipPlanViewSet, basename='membership-plan')

urlpatterns = [
    path('', include(router.urls)),
]
