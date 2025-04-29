from rest_framework import serializers
from .models import Staff, StaffRoles, StaffSalaryHistory

class RegularStaffSerializer(serializers.ModelSerializer):
    role = serializers.CharField(read_only=True)

    class Meta:
        model = Staff
        fields = [
            'id', 'email', 'first_name', 'last_name', 'phone_number',
            'department', 'salary', 'salary_credited_date',
            'role'
        ]

class SuperStaffSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    role = serializers.CharField(read_only=True)

    class Meta:
        model = Staff
        fields = [
            'id','email', 'first_name', 'last_name', 'phone_number',
            'address', 'department', 'salary', 'salary_credited_date',
            'salary_due_date', 'photo', 'role', 'password'
        ]

    def create(self, validated_data):
        password = validated_data.pop('password')
        staff = Staff.objects.create_superstaff(**validated_data, password=password)
        return staff


class StaffDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = '__all__'


class NestedStaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = [
            'id', 'email', 'first_name', 'last_name', 'phone_number',
            'address', 'department', 'salary', 'salary_credited_date',
            'salary_due_date', 'photo', 'role'
        ]


class StaffSalaryPaymentSerializer(serializers.ModelSerializer):
    staff = NestedStaffSerializer(read_only=True)

    class Meta:
        model = StaffSalaryHistory
        fields = [
            'id',
            'staff',
            'salary',
            'salary_credited_date',
            'salary_due_date',
            'created_at',
        ]
