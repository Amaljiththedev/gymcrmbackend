from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class RefreshTokenStore(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=512, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
