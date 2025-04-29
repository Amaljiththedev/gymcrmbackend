# serializers.py
from rest_framework import serializers
from .models import Trainer, TrainerSalaryHistory


class TrainerPaymenthistorySerializer(serializers.ModelSerializer):
    """Serializer for trainer payment history"""
    
    class Meta:
        model = TrainerSalaryHistory
        fields = [
            'id', 'trainer', 'salary',
            'salary_credited_date', 'salary_due_date', 'created_at'
        ]
        read_only_fields = ['id', 'trainer']


class TrainerSerializer(serializers.ModelSerializer):
    """Serializer for Trainer model"""
    payment_history = serializers.SerializerMethodField()

    class Meta:
        model = Trainer
        fields = [
            'id', 'name', 'email', 'phone_number', 'address',
            'salary', 'salary_credited_date', 'salary_due_date',
            'joined_date', 'photo', 'is_blocked', 'payment_history'
        ]

    def get_payment_history(self, obj):
        """Returns all salary payment records for a trainer"""
        history_qs = TrainerSalaryHistory.objects.filter(trainer=obj).order_by('-salary_credited_date')
        return TrainerPaymenthistorySerializer(history_qs, many=True).data


class NestedTrainerSerializer(serializers.ModelSerializer):
    """Nested serializer for Trainer model"""
    
    class Meta:
        model = Trainer
        fields = ['id', 'name', 'email', 'phone_number','photo','salary_due_date','salary','salary_credited_date','joined_date']

class TrainerSalaryHistorySerializer(serializers.ModelSerializer):
    trainer = NestedTrainerSerializer(read_only=True)

    class Meta:
        model = TrainerSalaryHistory
        fields = [
            'id', 'trainer', 'salary',
            'salary_credited_date', 'salary_due_date', 'created_at'
        ]

