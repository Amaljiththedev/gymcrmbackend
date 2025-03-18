from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

class StaffMember(models.Model):
    """
    Represents a staff member in the CRM.
    Stores non-authentication details such as personal information,
    employment details, and salary-related fields.
    """
    EMPLOYEE_ROLE_CHOICES = (
        ('super_staff', _('Super Staff')),  # Login-enabled staff with higher privileges.
        ('regular_staff', _('Regular Staff')),
    )

    employee_id = models.CharField(_('employee ID'), max_length=20, unique=True)
    first_name = models.CharField(_('first name'), max_length=100)
    last_name = models.CharField(_('last name'), max_length=100)
    email = models.EmailField(_('email address'), unique=True, null=True, blank=True)
    phone_number = models.CharField(_('phone number'), max_length=15, unique=True)
    address = models.TextField(_('address'), blank=True, null=True)
    role = models.CharField(_('role'), max_length=20, choices=EMPLOYEE_ROLE_CHOICES, default='regular_staff')
    department = models.CharField(_('department'), max_length=100, blank=True, null=True)
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)

    # Salary Details
    salary = models.DecimalField(_('salary'), max_digits=10, decimal_places=2)
    salary_due = models.DecimalField(_('salary due'), max_digits=10, decimal_places=2, default=0.00)
    salary_credited_day = models.PositiveSmallIntegerField(
        _('salary credited day'),
        validators=[MinValueValidator(1), MaxValueValidator(31)],
        help_text=_('Day of the month salary is credited (1-31)'),
        null=True,
        blank=True
    )
    last_salary_paid_on = models.DateField(_('Last Salary Paid On'), null=True, blank=True)
    is_salary_paid = models.BooleanField(_('Salary Paid'), default=False)

    is_active = models.BooleanField(_('active'), default=True)

    class Meta:
        ordering = ['employee_id']
        verbose_name = _('staff member')
        verbose_name_plural = _('staff members')

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.employee_id})"

class StaffUserManager(BaseUserManager):
    """
    Custom manager for StaffUser model.
    Provides helper methods for creating login-enabled staff users.
    """
    def create_staffuser(self, staff_member, password=None, **extra_fields):
        """
        Create and return a StaffUser linked to a StaffMember.
        The admin can set the password so that super staff can access
        the application and create new members.
        """
        if not staff_member.email:
            raise ValueError("Staff member must have an email to create a user account.")
        email_normalized = self.normalize_email(staff_member.email)
        user = self.model(staff_member=staff_member, email=email_normalized, **extra_fields)
        if password:
            user.set_password(password)
        else:
            raise ValueError("A password must be provided for a staff user.")
        user.save(using=self._db)
        return user

    def create_super_staffuser(self, staff_member, password, **extra_fields):
        """
        Create and return a super staff user with admin privileges.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_staffuser(staff_member, password, **extra_fields)

class StaffUser(AbstractBaseUser, PermissionsMixin):
    """
    Login-enabled staff model.
    Linked one-to-one with a StaffMember to separate authentication details
    from profile and employment information.
    """
    staff_member = models.OneToOneField(StaffMember, on_delete=models.CASCADE, related_name='user_account')
    email = models.EmailField(_('email address'), unique=True)
    is_staff = models.BooleanField(_('staff status'), default=False)
    is_active = models.BooleanField(_('active'), default=True)
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)

    # Override many-to-many fields to avoid reverse accessor clashes.
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='staffuser_groups',
        blank=True,
        help_text=_('The groups this user belongs to.'),
        verbose_name=_('groups')
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='staffuser_permissions',
        blank=True,
        help_text=_('Specific permissions for this user.'),
        verbose_name=_('user permissions')
    )

    objects = StaffUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Email and password are required by default

    class Meta:
        verbose_name = _('staff user')
        verbose_name_plural = _('staff users')

    def __str__(self):
        return self.email