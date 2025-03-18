from rest_framework import serializers
from .models import CustomUser

class UserProfileSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source='user_type')  # Map user_type to role

    class Meta:
        model = CustomUser
        fields = ['email', 'role']  # Make sure 'username' is removed
