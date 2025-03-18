from django.db import models
from django.utils import timezone
from datetime import timedelta

class MembershipPlan(models.Model):
    name = models.CharField(max_length=100)
    duration_days = models.PositiveIntegerField(help_text="Duration of the plan in days")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_locked = models.BooleanField(default=False, help_text="If locked, the plan cannot be modified once assigned.")

    def __str__(self):
        return f"{self.name} ({self.duration_days} days) - {self.price}"

class Member(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=False)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    height = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True,
                                   help_text="Height in centimeters")
    weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True,
                                   help_text="Weight in kilograms")
    dob = models.DateField(blank=True, null=True, help_text="Date of Birth")
    membership_start = models.DateTimeField(help_text="Manually set by the manager")
    membership_plan = models.ForeignKey(MembershipPlan, on_delete=models.CASCADE, help_text="Assigned membership plan")
    is_blocked = models.BooleanField(default=False, help_text="Mark if member is blocked")
    amount_paid = models.DecimalField(
        max_digits=10, decimal_places=2,
        default=0.00,
        help_text="Amount the member has paid so far"
    )
    photo = models.ImageField(upload_to='member_photos/', blank=True, null=True)  # New photo field

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def membership_end(self):
        """Calculate the membership end datetime based on the start and plan duration."""
        return self.membership_start + timedelta(days=self.membership_plan.duration_days)

    @property
    def is_fully_paid(self):
        return self.amount_paid >= self.membership_plan.price

    @property
    def membership_status(self):
        """
        Determine the current membership status:
          - "blocked" if the member is blocked.
          - "expired" if today's datetime is past membership_end.
          - "active" otherwise.
        """
        if self.is_blocked:
            return "blocked"
        if timezone.now() > self.membership_end:
            return "expired"
        return "active"

class Attendance(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='attendances')
    attendance_date = models.DateField(default=timezone.now)

    class Meta:
        unique_together = ('member', 'attendance_date')
        ordering = ['-attendance_date']

    def __str__(self):
        return f"{self.member} - {self.attendance_date}"
