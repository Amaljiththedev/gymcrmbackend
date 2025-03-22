from django.apps import AppConfig

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'interfaces.trainer'
    label = 'trainer'  # Use a simple label without dots
