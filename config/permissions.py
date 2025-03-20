from rest_framework import permissions

class IsManager(permissions.BasePermission):
    """
    Custom permission to allow only managers to access a view.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.user_type == 'manager')
