from django.apps import AppConfig

class MembersConfig(AppConfig):
    name = 'interfaces.members'
    label = 'members' 

    def ready(self):
        super().ready()
        # Import signals to register them
        import interfaces.members.signals
