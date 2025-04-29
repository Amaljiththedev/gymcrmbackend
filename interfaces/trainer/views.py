from rest_framework import viewsets, filters, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListAPIView
from django.shortcuts import get_object_or_404
from config.permissions import IsManager
from interfaces.trainer.models import Trainer, TrainerSalaryHistory
from interfaces.trainer.serializers import TrainerSerializer, TrainerPaymenthistorySerializer
from config.permissions import IsManager
from rest_framework import status 
from django.utils.dateformat import DateFormat
from django.utils.formats import get_format
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
# Trainer ViewSet to handle CRUD operations for Trainer
class TrainerViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows trainers to be viewed or edited.
    Provides CRUD operations for Trainer model.
    """
    queryset = Trainer.objects.all().prefetch_related('salary_history')
    serializer_class = TrainerSerializer
    permission_classes = [IsAuthenticated, IsManager]

    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['email', 'name']
    search_fields = ['email', 'name', 'phone_number']


# Trainer Detail View to handle viewing, updating, or deleting a single trainer
class TrainerDetailView(RetrieveUpdateDestroyAPIView):
    """
    API endpoint that allows a trainer to be viewed, updated, or deleted.
    """
    queryset = Trainer.objects.all().prefetch_related('salary_history')
    serializer_class = TrainerSerializer
    permission_classes = [IsAuthenticated, IsManager]


# Trainer List View to list all trainers
class TrainerListView(ListAPIView):
    """
    API endpoint that lists all trainers.
    """
    queryset = Trainer.objects.all().prefetch_related('salary_history')
    serializer_class = TrainerSerializer
    permission_classes = [IsAuthenticated, IsManager]

    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['email', 'name']
    search_fields = ['email', 'name', 'phone_number']


# Trainer Payment History ViewSet to handle CRUD operations for TrainerSalaryHistory
class TrainerPaymentHistoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows trainer payment history to be viewed, created, updated, or deleted.
    """
    queryset = TrainerSalaryHistory.objects.select_related('trainer').order_by('-created_at')
    serializer_class = TrainerPaymenthistorySerializer
    permission_classes = [IsAuthenticated, IsManager]

    @action(detail=False, methods=['get'], url_path='trainer/(?P<trainer_id>[^/.]+)')
    def by_trainer(self, request, trainer_id=None):
        """
        Get payment history for a specific trainer.
        """

        get_object_or_404(Trainer, pk=trainer_id)
        queryset = self.queryset.filter(trainer_id=trainer_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data ,status=status.HTTP_200_OK)



def generate_trainer_payment_history(request,history_id):
    """
    Generates a new salary payment history record for the given trainer.
    This function should be called whenever a trainer's salary is credited.
    """
    # Create a new salary history record


    try:
        record = TrainerSalaryHistory.objects.select_related('trainer').get(id=history_id)

        credited = DateFormat(record.salary_credited_date).format(get_format('DATE_FORMAT'))
        due = DateFormat(record.salary_due_date).format(get_format('DATE_FORMAT'))
        created = DateFormat(record.created_at).format(get_format('DATE_FORMAT'))

        context = {
            "id": record.id,
            "trainer": record.trainer.name,
            'email': record.trainer.email,
            'phone_number': record.trainer.phone_number,
            'salary': record.salary,
            'salary_credited_date': credited,
            'salary_due_date': due,
            'created_at': created,
        }

        html_string = render_to_string("trainerslip.html", context)
        pdf_file = HTML(string=html_string).write_pdf()

        response = HttpResponse(pdf_file, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="salary_slip_{history_id}.pdf"'
        return response

    except TrainerSalaryHistory.DoesNotExist:
        return HttpResponse("Salary history not found.", status=404)