from rest_framework import serializers
from .models import Member, Attendance, MembershipPlan, PaymentHistory

class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ['id', 'attendance_date']

class MembershipPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = MembershipPlan
        fields = '__all__'


class MemberSerializer(serializers.ModelSerializer):
    membership_plan = MembershipPlanSerializer(read_only=True)
    membership_plan_id = serializers.PrimaryKeyRelatedField(
        queryset=MembershipPlan.objects.all(),
        write_only=True,
        source='membership_plan'
    )
    days_present = serializers.SerializerMethodField(read_only=True)
    membership_status = serializers.SerializerMethodField(read_only=True)

    membership_end = serializers.ReadOnlyField()
    is_fully_paid = serializers.ReadOnlyField()
    remaining_balance = serializers.ReadOnlyField()
    biometric_id = serializers.ReadOnlyField()
    biometric_registered = serializers.ReadOnlyField()

    class Meta:
        model = Member
        fields = [
            'id', 'first_name', 'last_name', 'email', 'phone', 'address',
            'height', 'weight', 'dob', 'age', 'gender', 'membership_start',
            'membership_plan', 'membership_plan_id', 'membership_end',
            'is_blocked', 'amount_paid', 'remaining_balance', 'is_fully_paid',
            'days_present', 'photo', 'membership_status',
            'biometric_id', 'biometric_registered'  # 👈 added biometric fields
        ]

    def get_days_present(self, obj):
        return obj.attendances.count()

    def get_membership_status(self, obj):
        return obj.membership_status

class PaymentHistorySerializer(serializers.ModelSerializer):
    member_id = serializers.IntegerField(source='member.id', read_only=True)
    membership_plan_id = serializers.IntegerField(source='membership_plan.id', read_only=True)

    class Meta:
        model = PaymentHistory
        fields = [
            'id',
            'member_id',
            'membership_plan_id',
            'plan_name_snapshot',
            'plan_price_snapshot',
            'plan_duration_snapshot',
            'membership_start',
            'membership_end',
            'transaction_type',
            'payment_amount',
            'renewal_count',
            'transaction_date'
        ]
