from django.apps import AppConfig

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'interfaces.staff'
    label = 'staff'  # Use a simple label without dots
