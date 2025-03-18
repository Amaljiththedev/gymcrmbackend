from django.urls import path
from .views import (
    ManagerLoginView,
    StaffLoginView,
    LogoutView,
    UserProfileView,
    CSRFTokenView,
    AdminOnlyView,
    RefreshTokenView
)

urlpatterns = [
    path('login/manager/', ManagerLoginView.as_view(), name='manager_login'),
    path('login/staff/', StaffLoginView.as_view(), name='staff_login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('csrf/', CSRFTokenView.as_view(), name='csrf_token'),
    path('admin/', AdminOnlyView.as_view(), name='admin_only'),
    path('refresh/', RefreshTokenView.as_view(), name='refresh_token'),
]
