from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class CustomUserManager(BaseUserManager):
    def create_manager(self, email, password=None, **extra_fields):
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
        return self.create_manager(email=email, password=password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    user_type = models.CharField(max_length=10, default='manager', editable=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Manager"
        verbose_name_plural = "Managers"

    def __str__(self):
        return self.email

    def full_name(self):
        return f"{self.first_name or ''} {self.last_name or ''}".strip()

    def get_full_name(self):
        return self.full_name()

    def get_short_name(self):
        return self.first_name or self.email
