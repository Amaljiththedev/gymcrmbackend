from datetime import timezone
from rest_framework import serializers
from .models import Member, Attendance, MembershipPlan

class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ['id', 'attendance_date']


class MembershipPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = MembershipPlan
        fields = '__all__'


class MemberSerializer(serializers.ModelSerializer):
    # Read-only nested membership plan details
    membership_plan = MembershipPlanSerializer(read_only=True)
    # Write-only field to accept a membership plan ID
    membership_plan_id = serializers.PrimaryKeyRelatedField(
        queryset=MembershipPlan.objects.all(),
        write_only=True,
        source='membership_plan'
    )
    days_present = serializers.SerializerMethodField(read_only=True)
    membership_status = serializers.SerializerMethodField(read_only=True)
    membership_end = serializers.ReadOnlyField()
    is_fully_paid = serializers.ReadOnlyField()

    class Meta:
        model = Member
        fields = [
            'id', 'first_name', 'last_name', 'email', 'phone', 'address',
            'height', 'weight', 'dob', 'age', 'gender', 'membership_start',
            'membership_plan', 'membership_plan_id', 'membership_end',
            'is_blocked', 'amount_paid', 'is_fully_paid',
            'days_present', 'photo', 'membership_status'
        ]

    def get_days_present(self, obj):
        return obj.attendances.count()

    def get_membership_status(self, obj):
        # Use the model's property to keep logic in one place
        return obj.membership_status
