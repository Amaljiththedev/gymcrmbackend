from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class CustomUserManager(BaseUserManager):
    """
    Custom manager for CustomUser (Manager only).
    Provides helper methods for creating managers (including superusers).
    """
    
    def create_manager(self, email, password=None, **extra_fields):
        """
        Creates and returns a manager (CustomUser).
        """
        if not email:
            raise ValueError("Manager accounts must have an email address.")

        email = self.normalize_email(email)
        extra_fields.setdefault('user_type', 'manager')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        manager = self.model(email=email, **extra_fields)
        manager.set_password(password)
        manager.save(using=self._db)
        return manager

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Creates and returns a superuser with full permissions.
        """
        return self.create_manager(email=email, password=password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    CustomUser model for Managers only.
    - Uses email for authentication.
    - All managers have `is_staff=True` and `is_superuser=True`.
    """
    email = models.EmailField(unique=True)
    user_type = models.CharField(max_length=10, default='manager', editable=False)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)  # Allows access to Django admin.
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    # Login with email instead of username.
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Only email and password are required.

    class Meta:
        verbose_name = "Manager"
        verbose_name_plural = "Managers"

    def __str__(self):
        return self.email
