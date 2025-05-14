from django.db import models
from django.utils import timezone
from datetime import timedelta, date
from interfaces.members.services.biometric_service import register_member_on_biometric


class MembershipPlan(models.Model):
    name = models.CharField(max_length=100)
    duration_days = models.PositiveIntegerField(help_text="Duration of the plan in days")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_blocked = models.BooleanField(default=False, help_text="If blocked, cannot assign to new members.")

    def __str__(self):
        return f"{self.name} ({self.duration_days} days) - ₹{self.price}"


class Member(models.Model):
    GENDER_CHOICES = [('male', 'Male'), ('female', 'Female'), ('other', 'Other')]

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=False)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)

    height = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text="Height in cm")
    weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text="Weight in kg")
    dob = models.DateField(blank=True, null=True, help_text="Date of Birth")
    age = models.PositiveIntegerField(blank=True, null=True, help_text="Age in years")

    membership_start = models.DateTimeField(help_text="Manually set by the manager")
    membership_plan = models.ForeignKey(MembershipPlan, on_delete=models.SET_NULL, null=True, blank=True)
    membership_end = models.DateTimeField(blank=True, null=True, help_text="Auto-calculated on save")

    is_blocked = models.BooleanField(default=False)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    remaining_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, editable=False)
    renewal_count = models.PositiveIntegerField(default=0)

    biometric_id = models.IntegerField(unique=True, null=True, blank=True)
    biometric_registered = models.BooleanField(default=False)
    photo = models.ImageField(upload_to='member_photos/', blank=True, null=True)

    def save(self, *args, **kwargs):
        creating = self._state.adding

        # Membership dates & balance
        if self.membership_plan:
            self.membership_end = self.membership_start + timedelta(days=self.membership_plan.duration_days)
            if timezone.now() <= self.membership_end:
                self.remaining_balance = self.membership_plan.price - self.amount_paid
            else:
                self.remaining_balance = self.membership_plan.price
        else:
            self.remaining_balance = 0

        # Age from DOB
        if self.dob:
            today = date.today()
            self.age = today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))

        super().save(*args, **kwargs)

        # Assign biometric_id only once during creation
        if creating and not self.biometric_id:
            biometric_id = register_member_on_biometric(self)
            if biometric_id:
                self.biometric_id = biometric_id
                self.biometric_registered = False  # Will be true after device enrollment
                super().save(update_fields=['biometric_id', 'biometric_registered'])

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def is_fully_paid(self):
        return self.membership_plan and self.amount_paid >= self.membership_plan.price

    @property
    def membership_status(self):
        if self.is_blocked:
            return "blocked"
        if self.membership_end and timezone.now() > self.membership_end:
            return "expired"
        if self.membership_plan and self.amount_paid < self.membership_plan.price:
            return "payment_due"
        if self.membership_end and (self.membership_end - timezone.now() <= timedelta(days=5)):
            return "expiring"
        return "active"

    @property
    def can_access_gym(self):
        return (
            self.membership_status == "active"
            and not self.is_blocked
            and self.is_fully_paid
            and self.biometric_registered
        )

    class Meta:
        indexes = [
            models.Index(fields=['membership_start']),
            models.Index(fields=['membership_end']),
            models.Index(fields=['dob']),
        ]


class Attendance(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='attendances')
    attendance_date = models.DateField(default=timezone.now)

    class Meta:
        unique_together = ('member', 'attendance_date')
        ordering = ['-attendance_date']
        indexes = [
            models.Index(fields=['member']),
            models.Index(fields=['attendance_date']),
        ]

    def __str__(self):
        return f"{self.member} - {self.attendance_date}"


class PaymentHistory(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('initial', 'Initial Enrollment'),
        ('payment', 'Additional Payment'),
        ('renewal', 'Renewal'),
        ('plan_change', 'Plan Change'),
    ]
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='payment_history')
    membership_plan = models.ForeignKey(MembershipPlan, on_delete=models.SET_NULL, null=True, blank=True)
    plan_name_snapshot = models.CharField(max_length=100)
    plan_price_snapshot = models.DecimalField(max_digits=10, decimal_places=2)
    plan_duration_snapshot = models.PositiveIntegerField()
    membership_start = models.DateTimeField()
    membership_end = models.DateTimeField()
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES, default='payment')
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2)
    renewal_count = models.PositiveIntegerField(default=0)
    transaction_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.member} - {self.transaction_type} - ₹{self.payment_amount} (Cycle {self.renewal_count})"

    class Meta:
        ordering = ['-transaction_date']
