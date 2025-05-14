from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MemberViewSet,
    MembershipPlanViewSet,
    PaymentHistoryViewSet,
    active_members_view,
    download_invoice_detail,
    expired_members_view,
    expiring_members_view,
    members_to_register,
    not_fully_paid_members_view,
    mark_biometric_registered,
    sync_attendance_from_device
)

router = DefaultRouter()
router.register(r'members', MemberViewSet, basename='member')
router.register(r'membership-plans', MembershipPlanViewSet, basename='membership-plan')
router.register(r'payment-history', PaymentHistoryViewSet, basename='payment-history')


urlpatterns = [
    path('', include(router.urls)),
    path('active-members/', active_members_view, name='active-members'),
    path('expired-members/', expired_members_view, name='expired-members'),
    path('expiring-members/', expiring_members_view, name='expiring-members'),
    path('not-fully-paid-members/', not_fully_paid_members_view, name='not-fully-paid-members'),
    path('invoice/<int:member_id>/<int:invoice_id>/', download_invoice_detail, name='download-invoice-detail'),

        # Biometric API endpoints
    path('members-to-register/', members_to_register, name='members-to-register'),
    path('mark-registered/', mark_biometric_registered, name='mark-registered'),
    path('sync-biometric-attendance/', sync_attendance_from_device, name='biometric-attendance-sync'),



]
