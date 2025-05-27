from django.db import models
from django.conf import settings
import uuid

class Meeting(models.Model):
    ROOM_TYPE_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    type_of = models.CharField(max_length=10, choices=ROOM_TYPE_CHOICES, default='public')
    created_on = models.DateTimeField(auto_now_add=True)
    room_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return f"{self.title} - {self.user.email}"
