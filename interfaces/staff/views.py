from rest_framework.views import APIView
from rest_framework.response import Response
from .models import DepartmentChoices
from rest_framework import viewsets, filters, permissions
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListAPIView
from .models import Staff, StaffRoles
from .serializers import RegularStaffSerializer, SuperStaffSerializer, StaffDetailSerializer
from config.permissions import IsManager

class DepartmentListAPIView(APIView):
    """
    API endpoint that returns a list of department choices.
    """
    # Pre-compute the department list once, as it doesn't change.
    department_data = [{'value': value, 'label': label} for value, label in DepartmentChoices.choices]

    def get(self, request, format=None):
        return Response(self.department_data)

# Your existing viewsets
class RegularStaffViewSet(viewsets.ModelViewSet):
    serializer_class = RegularStaffSerializer
    queryset = Staff.objects.filter(role=StaffRoles.REGULAR).prefetch_related('groups', 'user_permissions')
    permission_classes = [permissions.IsAuthenticated, IsManager]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['email', 'first_name', 'last_name']
    search_fields = ['email', 'first_name', 'last_name', 'phone_number']

class SuperStaffViewSet(viewsets.ModelViewSet):
    serializer_class = SuperStaffSerializer
    queryset = Staff.objects.filter(role=StaffRoles.SUPER).prefetch_related('groups', 'user_permissions')
    permission_classes = [permissions.IsAuthenticated, IsManager]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['email', 'first_name', 'last_name']
    search_fields = ['email', 'first_name', 'last_name', 'phone_number']

class StaffDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Staff.objects.all()
    serializer_class = StaffDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsManager]

class AllStaffListView(ListAPIView):
    queryset = Staff.objects.all().prefetch_related('groups', 'user_permissions')
    serializer_class = StaffDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsManager]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['email', 'first_name', 'last_name']
    search_fields = ['email', 'first_name', 'last_name', 'phone_number']
