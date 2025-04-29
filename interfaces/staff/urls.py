from django.urls import path, include
from rest_framework.routers import DefaultRouter


from .views import StaffViewSet, StaffSalaryPaymentViewSet, RegularStaffViewSet, SuperStaffViewSet, DepartmentListAPIView , generate_salary_slip

router = DefaultRouter()
router.register(r'staff', StaffViewSet, basename='staff')
router.register(r'regular-staff', RegularStaffViewSet, basename='regular-staff')
router.register(r'super-staff', SuperStaffViewSet, basename='super-staff')
router.register(r'staff-salary-payments', StaffSalaryPaymentViewSet, basename='staff-salary-payments')

urlpatterns = [
    path('staff/departments/', DepartmentListAPIView.as_view(), name='department-list'),
    path("salary-slip/<int:history_id>/", generate_salary_slip, name="salary-slip"),
    path('', include(router.urls)),
]