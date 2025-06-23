from rest_framework import serializers
from .models import Meeting, Message, Signal, Recording, ParticipantState


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

class SignalSerializer(serializers.ModelSerializer):
    sender_email = serializers.ReadOnlyField(source='sender.email')

    class Meta:
        model = Signal
        fields = ['id', 'meeting', 'sender', 'sender_email', 'signal_type', 'data', 'created_at']
        read_only_fields = ['sender', 'sender_email', 'created_at']

class RecordingSerializer(serializers.ModelSerializer):
    uploaded_by_email = serializers.ReadOnlyField(source='uploaded_by.email')

    class Meta:
        model = Recording
        fields = ['id', 'meeting', 'uploaded_by', 'uploaded_by_email', 'file_url', 'created_at']
        read_only_fields = ['uploaded_by', 'uploaded_by_email', 'created_at']


class ParticipantStateSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source='user.email')

    class Meta:
        model = ParticipantState
        fields = [
            'id',
            'meeting',
            'user',
            'user_email',
            'audio_muted',
            'video_stopped',
            'in_call',
            'raised_hand',
            'screen_sharing',
        ]
        read_only_fields = ['meeting', 'user', 'user_email']
