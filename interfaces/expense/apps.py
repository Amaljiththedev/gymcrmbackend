from django.apps import AppConfig

class ExpenseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'interfaces.expense'  # Keep the full app path
    label = 'expense'  # This should be a unique simple label``