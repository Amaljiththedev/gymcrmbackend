from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DepartmentListAPIView,
    RegularStaffViewSet,
    SuperStaffViewSet,
    StaffDetailView,
    AllStaffListView
)

router = DefaultRouter()
router.register(r'regular-staff', RegularStaffViewSet, basename='regular-staff')
router.register(r'super-staff', SuperStaffViewSet, basename='super-staff')

urlpatterns = [
    path('departments/', DepartmentListAPIView.as_view(), name='department-list'),
    path('', include(router.urls)),
    path('staff/<int:pk>/', StaffDetailView.as_view(), name='staff-detail'),
    path('all-staff/', AllStaffListView.as_view(), name='all-staff'),
]
