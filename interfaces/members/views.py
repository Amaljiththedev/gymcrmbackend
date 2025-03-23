from datetime import timedelta
from django.utils import timezone
from django.db.models import F, ExpressionWrapper, DurationField, Count
from django.db.models.functions import Now
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Member, Attendance, MembershipPlan
from .serializers import MemberSerializer, MembershipPlanSerializer
from .cache_utils import get_active_members, get_expired_members, get_expiring_members, get_not_fully_paid_members

class MemberViewSet(viewsets.ModelViewSet):
    """
    ViewSet to manage gym members with features such as:
      - Blocking members
      - Marking attendance via biometric verification
      - Standard CRUD operations
      - Filtering expiring, expired, active, and not fully paid memberships
    """
    serializer_class = MemberSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Optimize by selecting related membership_plan and prefetching attendances,
        # and annotate attendance_count to avoid extra queries when counting.
        return Member.objects.select_related('membership_plan')\
                             .prefetch_related('attendances')\
                             .annotate(attendance_count=Count('attendances'))

    def perform_create(self, serializer):
        serializer.save()

    def update(self, request, *args, **kwargs):
        # Prevent updates to blocked members.
        member = self.get_object()
        if member.is_blocked:
            return Response({'error': 'Blocked members cannot be updated.'},
                            status=status.HTTP_400_BAD_REQUEST)
        return super().update(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def block(self, request, pk=None):
        """Block a member from accessing the gym."""
        member = self.get_object()
        if member.is_blocked:
            return Response({'detail': 'Member is already blocked.'}, status=status.HTTP_200_OK)
        member.is_blocked = True
        member.save()
        return Response({'detail': 'Member blocked successfully.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def mark_attendance(self, request, pk=None):
        """
        Mark attendance for the member via biometric verification.
        Expected payload should include a 'biometric_token' or similar.
        """
        member = self.get_object()
        biometric_token = request.data.get('biometric_token')
        if not biometric_token:
            return Response({'error': 'Biometric token is required.'},
                            status=status.HTTP_400_BAD_REQUEST)
        # TODO: Add biometric verification logic here. For now, assume it's valid.
        today = timezone.now().date()
        attendance, created = Attendance.objects.get_or_create(member=member, attendance_date=today)
        if created:
            return Response({'detail': 'Attendance marked via biometrics.'},
                            status=status.HTTP_201_CREATED)
        return Response({'detail': 'Attendance already marked for today.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def attendance(self, request, pk=None):
        """Return total days attended by the member using annotated attendance_count."""
        member = self.get_object()
        return Response({'days_present': member.attendance_count}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def expiring_members(self, request):
        """
        Fetch members whose memberships are expiring within the next 5 days.
        Annotates each member with remaining duration (DurationField) and filters accordingly.
        """
        queryset = self.get_queryset().filter(membership_end__isnull=False).annotate(
            days_remaining=ExpressionWrapper(F('membership_end') - Now(),
                                             output_field=DurationField())
        ).filter(days_remaining__lte=timedelta(days=5), days_remaining__gte=timedelta(days=0))
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def expired_members(self, request):
        """Fetch members whose memberships have already expired."""
        today = timezone.now()
        queryset = self.get_queryset().filter(membership_end__lt=today)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def active_members(self, request):
        """Fetch members whose memberships are currently active."""
        today = timezone.now()
        queryset = self.get_queryset().filter(membership_end__gte=today, is_blocked=False)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def not_fully_paid(self, request):
        """Fetch members who have not paid in full."""
        queryset = self.get_queryset().filter(
            amount_paid__lt=F('membership_plan__price')
        ).exclude(amount_paid__isnull=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MembershipPlanViewSet(viewsets.ModelViewSet):
    """
    ViewSet to manage membership plans.
    """
    queryset = MembershipPlan.objects.all()
    serializer_class = MembershipPlanSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)


# --- Cached API Endpoints ---

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def active_members_view(request):
    data = get_active_members()
    return Response(data, status=200)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def expired_members_view(request):
    data = get_expired_members()
    return Response(data, status=200)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def expiring_members_view(request):
    data = get_expiring_members()
    return Response(data, status=200)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def not_fully_paid_members_view(request):
    data = get_not_fully_paid_members()
    return Response(data, status=200)