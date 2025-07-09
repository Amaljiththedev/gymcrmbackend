from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
from datetime import timedelta

def get_default_salary_due_date():
    # Salary is credited monthly; thus, default due date is set to 31 days from now.
    return timezone.now() + timedelta(days=31)

class Trainer(models.Model):
    """
    Trainer model representing a trainer in the system.
    """
    # Basic Information
    name = models.CharField(max_length=100, verbose_name="Trainer Name")
    email = models.EmailField(unique=True, verbose_name="Email Address")
    photo = models.ImageField(upload_to='trainer_photos/', blank=True, null=True, verbose_name="Profile Photo")
    
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=17,
        blank=True,
        null=True,
        verbose_name="Phone Number"
    )
    address = models.CharField(max_length=200, blank=True, null=True, verbose_name="Address")
    
    # Financial Information
    salary = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Salary")
    salary_credited_date = models.DateTimeField(default=timezone.now, verbose_name="Salary Credited Date")
    salary_due_date = models.DateTimeField(default=get_default_salary_due_date, verbose_name="Salary Due Date")
    
    # Other Information
    joined_date = models.DateTimeField(auto_now_add=True, verbose_name="Date Joined")
    photo = models.ImageField(upload_to='trainer_photos/', blank=True, null=True, verbose_name="Profile Photo")
    is_blocked = models.BooleanField(default=False, help_text="Mark if trainer is blocked", verbose_name="Blocked Status")
    
    class Meta:
        ordering = ['name']
        verbose_name = "Trainer"
        verbose_name_plural = "Trainers"
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['phone_number']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.email})"
    
    def block_trainer(self):
        """
        Blocks the trainer.
        """
        self.is_blocked = True
        self.save(update_fields=['is_blocked'])
    
    def unblock_trainer(self):
        """
        Unblocks the trainer.
        """
        self.is_blocked = False
        self.save(update_fields=['is_blocked'])
    
    def update_salary_due_date(self):
        """
        Updates the salary due date based on the current salary credited date.
        """
        self.salary_due_date = self.salary_credited_date + timedelta(days=31)
        self.save(update_fields=['salary_due_date'])



class TrainerSalaryHistory(models.Model):
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, related_name='salary_history')
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    salary_credited_date = models.DateTimeField(default=timezone.now)
    salary_due_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Salary history for {self.Trainer.name} - ₹{self.salary}"
    
    class Meta:
        ordering = ['-created_at']
    
