from rest_framework import serializers

from authentication.models import User
from .models import CustomUser

class UserProfileSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source='user_type')  # Map user_type to role

    class Meta:
        model = CustomUser
        fields = ['email', 'role']  # Make sure 'username' is removed


class ManagerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'profile_picture']
        read_only_fields = ['email']


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=6)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value

    def validate_new_password(self, value):
        if len(value) < 6:
            raise serializers.ValidationError("New password must be at least 6 characters long.")
        return value
    
