from rest_framework import serializers
from .models import Staff, StaffRoles

class RegularStaffSerializer(serializers.ModelSerializer):
    # Role is read-only (will always be "regular_staff" for this serializer)
    role = serializers.CharField(read_only=True)

    class Meta:
        model = Staff
        fields = [
            'id', 'email', 'first_name', 'last_name', 'phone_number',
            'department', 'salary', 'salary_credited_day', 'role'
        ]


class SuperStaffSerializer(serializers.ModelSerializer):
    # Super staff require a password on creation
    password = serializers.CharField(write_only=True, required=True)
    role = serializers.CharField(read_only=True)

    class Meta:
        model = Staff
        fields = [
            'id', 'email', 'first_name', 'last_name', 'phone_number',
            'department', 'salary', 'salary_credited_day', 'role', 'password'
        ]

    def create(self, validated_data):
        password = validated_data.pop('password')
        # Use the custom manager's create_superstaff method to set is_staff and is_superuser
        staff = Staff.objects.create_superstaff(**validated_data, password=password)
        return staff


class StaffDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving a single staff member's details,
    used in the StaffDetailView and for listing all staff.
    """
    class Meta:
        model = Staff
        fields = '__all__'
