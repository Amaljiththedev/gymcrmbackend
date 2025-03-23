from datetime import timedelta
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
    Group,
    Permission
)

# =============================================================================
# Trainer & Trainer Attendance Models
# =============================================================================

class Trainer(models.Model):
    """
    Model representing a trainer with salary details and biometric integration.
    """
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    joined_date = models.DateField(default=timezone.now)
    photo = models.ImageField(upload_to='trainers/', blank=True, null=True)
    salary_credited_date = models.DateField(default=timezone.now)
    salary_due_date = models.DateField(blank=True, null=True)
    biometric_id = models.CharField(
        max_length=50, unique=True, blank=True, null=True,
        help_text="Unique ID from the biometric device"
    )

    def save(self, *args, **kwargs):
        """
        Automatically sets salary_due_date if not provided.
        """
        if not self.salary_due_date:
            self.salary_due_date = self.salary_credited_date + timedelta(days=30)
        super().save(*args, **kwargs)

    def update_salary_due_date(self):
        """
        Update salary_due_date for the next month.
        """
        self.salary_credited_date = timezone.now().date()
        self.salary_due_date = self.salary_credited_date + timedelta(days=30)
        self.save()

    def pay_salary(self):
        """
        Log this trainer's salary as an expense and update salary dates.
        """
        Expense.objects.create(
            title=f"Trainer Salary - {self.name}",
            amount=self.salary,
            category="salary",
            description=f"Monthly salary for {self.name} (Trainer)",
            expense_source="trainer"
        )
        self.salary_credited_date = timezone.now().date()
        self.salary_due_date = self.salary_credited_date + timedelta(days=30)
        self.save()

    def __str__(self):
        return f"Trainer: {self.name}, Salary: ₹{self.salary}, Next Payment: {self.salary_due_date}"


class TrainerAttendance(models.Model):
    """
    Model representing trainer attendance.
    """
    trainer = models.ForeignKey(
        Trainer, on_delete=models.CASCADE, related_name="attendances"
    )
    date = models.DateField(default=timezone.now)
    check_in_time = models.DateTimeField(blank=True, null=True)
    check_out_time = models.DateTimeField(blank=True, null=True)
    total_hours = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    status = models.CharField(
        max_length=10,
        choices=[('Present', 'Present'), ('Absent', 'Absent'), ('Late', 'Late')],
        default='Absent'
    )

    def save(self, *args, **kwargs):
        """
        Auto-check-out after 12 hours if check-out is missing.
        Calculates total hours and updates attendance status.
        """
        if self.check_in_time and not self.check_out_time:
            auto_checkout_time = self.check_in_time + timedelta(hours=12)
            if timezone.now() > auto_checkout_time:
                self.check_out_time = auto_checkout_time

        if self.check_in_time and self.check_out_time:
            duration = self.check_out_time - self.check_in_time
            self.total_hours = round(duration.total_seconds() / 3600, 2)

        if self.check_in_time and not self.check_out_time:
            self.status = 'Present'

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.trainer.name} - {self.date} - {self.status}"