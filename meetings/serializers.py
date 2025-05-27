from rest_framework import serializers
from .models import Meeting
from .models import Message

class MessageSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source='user.email')
    class Meta:
        model = Message
        fields = ['id', 'meeting', 'user', 'user_email', 'content', 'timestamp']
        read_only_fields = ['user', 'user_email', 'timestamp']


class MeetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = '__all__'
        read_only_fields = ['user', 'created_on', 'room_id']