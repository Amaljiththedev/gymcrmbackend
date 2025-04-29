from django.utils import timezone
from django.db import models

class Expense(models.Model):
    CATEGORY_CHOICES = [
        ('salary', 'Salary Payment'),
        ('equipment', 'Equipment Purchase'),
        ('maintenance', 'Maintenance'),
        ('utilities', 'Utilities'),
        ('rent', 'Rent'),
        ('marketing', 'Marketing'),
        ('other', 'Other'),
    ]

    EXPENSE_SOURCE_CHOICES = [
        ('trainer', 'Trainer'),
        ('staff', 'Staff'),
        ('other', 'Other'),
    ]

    title = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(
        max_length=50, 
        choices=CATEGORY_CHOICES, 
        default='other', 
        db_index=True
    )
    description = models.TextField(blank=True, null=True)
    date = models.DateField(default=timezone.now, db_index=True)
    expense_source = models.CharField(
        max_length=20, 
        choices=EXPENSE_SOURCE_CHOICES, 
        default='other', 
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return f"{self.title} - ₹{self.amount} ({self.category})"

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category', 'date']),
            models.Index(fields=['expense_source', 'date']),
            # Explicit index on created_at is redundant if already set in the field,
            # but included here to illustrate custom composite indexes.
            models.Index(fields=['created_at']),
        ]


