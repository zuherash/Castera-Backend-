from django.db import models
from django.conf import settings
import uuid

class Meeting(models.Model):
    ROOM_TYPE_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('ended', 'Ended'),
    ]


    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    type_of = models.CharField(max_length=10, choices=ROOM_TYPE_CHOICES, default='public')
    created_on = models.DateTimeField(auto_now_add=True)
    room_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')

    def __str__(self):
        return f"{self.title} - {self.user.email}"
class Message(models.Model):
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.user.email} in {self.meeting.title}"
    
class Signal(models.Model):
    SIGNAL_TYPE_CHOICES = [
        ('offer', 'Offer'),
        ('answer', 'Answer'),
        ('ice', 'ICE'),
    ]

    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='signals')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    signal_type = models.CharField(max_length=10, choices=SIGNAL_TYPE_CHOICES)
    data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.signal_type.upper()} by {self.sender.email} in {self.meeting.title}"
