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
    # Write-only field to accept a membership plan ID from the frontend
    membership_plan_id = serializers.PrimaryKeyRelatedField(
        queryset=MembershipPlan.objects.all(),
        write_only=True,
        source='membership_plan'
    )
    days_present = serializers.SerializerMethodField(read_only=True)
    membership_end = serializers.ReadOnlyField()
    is_fully_paid = serializers.ReadOnlyField()
    photo = serializers.ImageField(required=False)

    class Meta:
        model = Member
        fields = [
             'id','first_name', 'last_name', 'email', 'phone', 'address',
            'height', 'weight', 'dob', 'membership_start', 
            'membership_plan', 'membership_plan_id',
            'is_blocked', 'amount_paid', 'membership_end', 'is_fully_paid',
            'days_present', 'photo','membership_status'
        ]

    def get_days_present(self, obj):
        return obj.attendances.count()
    
    def get_membership_status(self, obj):
        if obj.is_blocked:
            return "blocked"
        elif timezone.now() > obj.membership_end:
            return "expired"
        else:
            return "active"