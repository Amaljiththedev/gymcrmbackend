from rest_framework import serializers
from .models import Staff, StaffRoles

class RegularStaffSerializer(serializers.ModelSerializer):
    role = serializers.CharField(read_only=True)  # Role is read-only

    class Meta:
        model = Staff
        fields = [
            'id', 'email', 'first_name', 'last_name', 'phone_number',
            'department', 'salary', 'salary_credited_date',  # ✅ Fixed field name
            'role'
        ]


class SuperStaffSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)  # ✅ Ensure password field is included
    role = serializers.CharField(read_only=True)

    class Meta:
        model = Staff
        fields = [
            'email', 'first_name', 'last_name', 'phone_number',
            'address', 'department', 'salary', 'salary_credited_date',
            'salary_due_date', 'photo', 'role', 'password'  # ✅ Include password field
        ]

    def create(self, validated_data):
        password = validated_data.pop('password')
        staff = Staff.objects.create_superstaff(**validated_data, password=password)
        return staff


class StaffDetailSerializer(serializers.ModelSerializer):
    """Serializer for retrieving a single staff member's details."""
    
    class Meta:
        model = Staff
        fields = '__all__'
