from django.utils import timezone
from django.db import models

# Create your models here.
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
    trainer = models.ForeignKey("trainer.Trainer", on_delete=models.SET_NULL, null=True, blank=True)
    staff = models.ForeignKey("staff.Staff", on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    description = models.TextField(blank=True, null=True)
    date = models.DateField(default=timezone.now)
    expense_source = models.CharField(
        max_length=20,
        choices=EXPENSE_SOURCE_CHOICES,
        default='other'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - ₹{self.amount} ({self.category})"