from datetime import timedelta
from django.utils import timezone
from django.db.models import F, ExpressionWrapper, DateField
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models.functions import Cast
from .models import Member, Attendance, MembershipPlan
from .serializers import MemberSerializer, MembershipPlanSerializer

class MemberViewSet(viewsets.ModelViewSet):
    """
    ViewSet to manage gym members.

    Features:
    - Fetching expiring members (membership ending in ≤5 days)
    - Fetching expired members
    - Fetching active members
    - Fetching members with incomplete payments
    - Blocking members
    - Attendance tracking
    """
    serializer_class = MemberSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Optimized query to prefetch related membership plans and attendance data."""
        return Member.objects.select_related('membership_plan').prefetch_related('attendances').all()

    def perform_create(self, serializer):
        """Handles member creation."""
        serializer.save()

    def update(self, request, *args, **kwargs):
        """Prevents updating blocked members."""
        member = self.get_object()
        if member.is_blocked:
            return Response({'error': 'Blocked members cannot be updated.'}, status=status.HTTP_400_BAD_REQUEST)
        return super().update(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def block(self, request, pk=None):
        """Blocks a member from accessing the gym."""
        member = self.get_object()
        if member.is_blocked:
            return Response({'detail': 'Member is already blocked.'}, status=status.HTTP_200_OK)
        member.is_blocked = True
        member.save()
        return Response({'detail': 'Member blocked successfully.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def add_attendance(self, request, pk=None):
        """Records attendance for a member."""
        member = self.get_object()
        today = timezone.now().date()
        attendance, created = Attendance.objects.get_or_create(member=member, attendance_date=today)
        if created:
            return Response({'detail': 'Attendance recorded for today.'}, status=status.HTTP_201_CREATED)
        return Response({'detail': 'Attendance already recorded for today.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def attendance(self, request, pk=None):
        """Returns total days a member has attended."""
        member = self.get_object()
        days_present = member.attendances.count()
        return Response({'days_present': days_present}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def expiring_members(self, request):
        """
        Fetches members whose memberships are expiring within the next 5 days.
        Excludes already expired members.
        """
        today = timezone.now().date()
        upcoming_expiry_date = today + timedelta(days=5)

        queryset = self.get_queryset().annotate(
            db_membership_end=ExpressionWrapper(
                Cast(F('membership_start'), DateField()) + ExpressionWrapper(
                    F('membership_plan__duration_days') * timedelta(days=1),
                    output_field=DateField()
                ),
                output_field=DateField()
            )
        ).filter(
            db_membership_end__gte=today,
            db_membership_end__lte=upcoming_expiry_date
        )

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def expired_members(self, request):
        """Fetches members whose memberships have already expired."""
        today = timezone.now().date()

        queryset = self.get_queryset().annotate(
            db_membership_end=ExpressionWrapper(
                F('membership_start') + ExpressionWrapper(
                    F('membership_plan__duration_days') * timedelta(days=1),
                    output_field=DateField()
                ),
                output_field=DateField()
            )
        ).filter(db_membership_end__lt=today)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def active_members(self, request):
        """
        Fetches members whose memberships are currently active.
        """
        today = timezone.now().date()

        queryset = self.get_queryset().annotate(
            db_membership_end=ExpressionWrapper(
                F('membership_start') + ExpressionWrapper(
                    F('membership_plan__duration_days') * timedelta(days=1),
                    output_field=DateField()
                ),
                output_field=DateField()
            )
        ).filter(
            db_membership_end__gte=today,  # Membership is still valid
            is_blocked=False  # Exclude blocked members
        )

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def not_fully_paid(self, request):
        """
        Fetches members who have not paid in full.
        """
        queryset = self.get_queryset().filter(
            amount_paid__lt=F('membership_plan__price')
        ).exclude(amount_paid__isnull=True)  # Exclude NULL values explicitly

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class MembershipPlanViewSet(viewsets.ModelViewSet):
    """
    ViewSet to manage membership plans.
    Prevents updating locked plans.
    """
    queryset = MembershipPlan.objects.all()
    serializer_class = MembershipPlanSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        """Prevents updating locked membership plans."""
        instance = self.get_object()
        if instance.is_locked:
            return Response({'error': 'This membership plan is locked and cannot be modified.'}, status=status.HTTP_400_BAD_REQUEST)
        return super().update(request, *args, **kwargs)
