from rest_framework import viewsets, filters, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListAPIView
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.http import HttpResponse
from weasyprint import HTML
from .models import StaffSalaryHistory
from .models import Staff, StaffRoles, StaffSalaryHistory, DepartmentChoices
from .serializers import RegularStaffSerializer, SuperStaffSerializer, StaffDetailSerializer, StaffSalaryPaymentSerializer
from config.permissions import IsManager
from rest_framework import status 
from django.utils.dateformat import DateFormat
from django.utils.formats import get_format

class DepartmentListAPIView(APIView):
    """
    API endpoint that returns a list of department choices.
    """
    # Pre-compute the department list once, as it doesn't change.
    department_data = [{'value': value, 'label': label} for value, label in DepartmentChoices.choices]

    def get(self, request, format=None):
        return Response(self.department_data)

# Regular Staff Viewset
class RegularStaffViewSet(viewsets.ModelViewSet):
    serializer_class = RegularStaffSerializer
    queryset = Staff.objects.filter(role=StaffRoles.REGULAR).prefetch_related('groups', 'user_permissions')
    permission_classes = [IsAuthenticated, IsManager]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['email', 'first_name', 'last_name']
    search_fields = ['email', 'first_name', 'last_name', 'phone_number']

# Super Staff Viewset
class SuperStaffViewSet(viewsets.ModelViewSet):
    serializer_class = SuperStaffSerializer
    queryset = Staff.objects.filter(role=StaffRoles.SUPER).prefetch_related('groups', 'user_permissions')
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['email', 'first_name', 'last_name']
    search_fields = ['email', 'first_name', 'last_name', 'phone_number']

# Staff Detail View
class StaffDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Staff.objects.all()
    serializer_class = StaffDetailSerializer
    permission_classes = [IsAuthenticated]

# List All Staff
class AllStaffListView(ListAPIView):
    queryset = Staff.objects.all().prefetch_related('groups', 'user_permissions')
    serializer_class = StaffDetailSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['email', 'first_name', 'last_name']
    search_fields = ['email', 'first_name', 'last_name', 'phone_number']

# Staff Viewset
class StaffViewSet(viewsets.ModelViewSet):
    queryset = Staff.objects.all()
    serializer_class = StaffDetailSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def regular_staff(self, request):
        queryset = Staff.objects.filter(role=StaffRoles.REGULAR)
        serializer = RegularStaffSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def super_staff(self, request):
        queryset = Staff.objects.filter(role=StaffRoles.SUPER)
        serializer = SuperStaffSerializer(queryset, many=True)
        return Response(serializer.data)

# Staff Salary Payment Viewset



class StaffSalaryPaymentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A read-only viewset for StaffSalaryHistory records.
    This endpoint provides:
      - Standard list and retrieve operations.
      - A custom action to filter by staff member.
    """
    queryset = StaffSalaryHistory.objects.select_related('staff').order_by('-created_at')
    serializer_class = StaffSalaryPaymentSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='staff/(?P<staff_id>[^/.]+)')
    def by_staff(self, request, staff_id=None):
        """
        Returns the salary history for a specific staff member.
        """
        get_object_or_404(Staff, pk=staff_id)
        queryset = self.get_queryset().filter(staff__id=staff_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    


def generate_salary_slip(request, history_id):
    try:
        record = StaffSalaryHistory.objects.select_related("staff").get(id=history_id)

        # Format dates
        credited = DateFormat(record.salary_credited_date).format(get_format('DATE_FORMAT'))
        due = DateFormat(record.salary_due_date).format(get_format('DATE_FORMAT'))
        created = DateFormat(record.created_at).format('d M Y, H:i')

        context = {
            "id": record.id,
            "staff_name": f"{record.staff.first_name} {record.staff.last_name}",
            "email": record.staff.email,
            "amount": record.salary,
            "credited_date": credited,
            "due_date": due,
            "created_at": created,
        }

        html_string = render_to_string("salary_slip_template.html", context)
        pdf_file = HTML(string=html_string).write_pdf()

        response = HttpResponse(pdf_file, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="salary_slip_{history_id}.pdf"'
        return response

    except StaffSalaryHistory.DoesNotExist:
        return HttpResponse("Salary history not found.", status=404)