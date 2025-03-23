from rest_framework import viewsets, permissions
from .models import Trainer
from .serializers import TrainerSerializer

class TrainerViewSet(viewsets.ModelViewSet):
    """
    A viewset that provides CRUD operations for Trainer.
    Only authenticated users are allowed.
    """
    queryset = Trainer.objects.all()
    serializer_class = TrainerSerializer
    permission_classes = [permissions.IsAuthenticated]