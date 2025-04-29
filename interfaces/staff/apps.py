from django.apps import AppConfig

class StaffConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'interfaces.staff'
    label = 'staff'  # Use a simple label without dots

    def ready(self):
        import interfaces.staff.signals  # Optional: include if using signals



