from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.models import Group, Permission

class StaffRoles(models.TextChoices):
    REGULAR = 'regular_staff', 'Regular Staff'
    SUPER = 'super_staff', 'Super Staff'


class DepartmentChoices(models.TextChoices):
    FRONT_DESK = 'front_desk', 'Front Desk'
    CLEANING = 'cleaning', 'Cleaning Staff'
    MAINTENANCE = 'maintenance', 'Maintenance'
    ACCOUNTING = 'accounting', 'Accounting'
    SECURITY = 'security', 'Security'
    SALES = 'sales', 'Sales & Marketing'
    CUSTOMER_SERVICE = 'customer_service', 'Customer Service'


class StaffManager(BaseUserManager):
    def create_staff(self, email, first_name, last_name, phone_number, address, department, salary, salary_credited_date, photo, salary_due_date=None, role=StaffRoles.REGULAR, password=None):
        if not email:
            raise ValueError("Staff must have an email address")
        email = self.normalize_email(email)
        if salary_due_date is None:
            salary_due_date = salary_credited_date + timedelta(days=30)
        staff = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            address=address,
            department=department,
            salary=salary,
            salary_credited_date=salary_credited_date,
            salary_due_date=salary_due_date,
            photo=photo,
            role=role,
        )
        if password:
            staff.set_password(password)
        staff.save(using=self._db)
        return staff

    def create_superstaff(self, email, first_name, last_name, phone_number, address, department, salary, salary_credited_date, photo, salary_due_date=None, password=None):
        staff = self.create_staff(email, first_name, last_name, phone_number, address, department, salary, salary_credited_date, photo, salary_due_date=salary_due_date, role=StaffRoles.SUPER, password=password)
        staff.is_superuser = True
        staff.is_staff = True
        staff.save(using=self._db)
        return staff


class Staff(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, db_index=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15, db_index=True)
    address = models.TextField(blank=True, null=True)
    department = models.CharField(max_length=20, choices=DepartmentChoices.choices, db_index=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    salary_credited_date = models.DateField(default=timezone.now)
    salary_due_date = models.DateField(blank=True, null=True)
    photo = models.ImageField(upload_to='staff_photos/')
    role = models.CharField(max_length=20, choices=StaffRoles.choices, default=StaffRoles.REGULAR, db_index=True)

    # Explicit related names for groups and permissions
    groups = models.ManyToManyField(Group, related_name="staff_members", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="staff_permissions", blank=True)

    objects = StaffManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone_number', 'department', 'salary', 'salary_credited_date', 'photo']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.get_role_display()})"

    def save(self, *args, **kwargs):
        if not self.salary_due_date:
            self.salary_due_date = self.salary_credited_date + timedelta(days=30)
        super().save(*args, **kwargs)


class StaffSalaryHistory(models.Model):
    staff = models.ForeignKey('Staff', on_delete=models.CASCADE)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    salary_credited_date = models.DateField(default=timezone.now)
    salary_due_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Salary history for {self.staff.first_name} {self.staff.last_name} - ₹{self.salary}"

    class Meta:
        ordering = ['-created_at']