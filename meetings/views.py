from rest_framework import viewsets, permissions, generics, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.utils import timezone
from .models import Meeting, Message, Signal, Recording, ParticipantState
from .serializers import (
    MeetingSerializer,
    MessageSerializer,
    SignalSerializer,
    RecordingSerializer,
    ParticipantStateSerializer,
)
from .permissions import IsOwnerOrAdmin
from rest_framework.permissions import SAFE_METHODS
from rest_framework.views import APIView


# الانضمام إلى اجتماع عبر room_id (UUID)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def join_meeting(request, room_id):
    try:
        meeting = Meeting.objects.get(room_id=room_id)
    except Meeting.DoesNotExist:
        return Response({'error': 'Meeting not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = MeetingSerializer(meeting)
    return Response(serializer.data)


#  إدارة الاجتماعات
class MeetingViewSet(viewsets.ModelViewSet):
    serializer_class = MeetingSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        queryset = Meeting.objects.all().order_by('-created_on')
        if user.role == 'admin':
            return queryset
        if getattr(self, 'action', None) == 'list':
            return queryset.filter(user=user)
        if self.request.method in SAFE_METHODS:
            return queryset
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'], url_path='set-status')
    def set_status(self, request, pk=None):
        meeting = self.get_object()
        new_status = request.data.get('status')

        if new_status not in ['active', 'ended']:
            return Response({'error': 'Invalid status'}, status=400)

        meeting.status = new_status
        meeting.save()
        return Response({'message': f'Status set to {new_status}'})

    @action(detail=True, methods=['post'], url_path='mute-audio')
    def mute_audio(self, request, pk=None):
        """Mute the authenticated user's microphone in the meeting."""
        meeting = self.get_object()
        state, _ = ParticipantState.objects.get_or_create(
            meeting=meeting, user=request.user
        )
        state.audio_muted = True
        state.save()
        return Response({'message': 'Audio muted'})

    @action(detail=True, methods=['post'], url_path='stop-video')
    def stop_video(self, request, pk=None):
        """Stop the authenticated user's video in the meeting."""
        meeting = self.get_object()
        state, _ = ParticipantState.objects.get_or_create(
            meeting=meeting, user=request.user
        )
        state.video_stopped = True
        state.save()
        return Response({'message': 'Video stopped'})

    @action(detail=True, methods=['post'], url_path='stop-call')
    def stop_call(self, request, pk=None):
        """Mark that the authenticated user has left the call."""
        meeting = self.get_object()
        state, _ = ParticipantState.objects.get_or_create(
            meeting=meeting, user=request.user
        )
        state.in_call = False
        state.save()
        return Response({'message': 'Call stopped'})

    @action(detail=True, methods=['post'], url_path='raise-hand')
    def raise_hand(self, request, pk=None):
        """Raise the authenticated user's hand."""
        meeting = self.get_object()
        state, _ = ParticipantState.objects.get_or_create(
            meeting=meeting, user=request.user
        )
        state.raised_hand = True
        state.save()
        return Response({'message': 'Hand raised'})

    @action(detail=True, methods=['post'], url_path='lower-hand')
    def lower_hand(self, request, pk=None):
        """Lower the authenticated user's hand."""
        meeting = self.get_object()
        state, _ = ParticipantState.objects.get_or_create(
            meeting=meeting, user=request.user
        )
        state.raised_hand = False
        state.save()
        return Response({'message': 'Hand lowered'})

    @action(detail=True, methods=['post'], url_path='start-screen-share')
    def start_screen_share(self, request, pk=None):
        """Mark that the authenticated user started screen sharing."""
        meeting = self.get_object()
        state, _ = ParticipantState.objects.get_or_create(
            meeting=meeting, user=request.user
        )
        state.screen_sharing = True
        state.save()
        return Response({'message': 'Screen sharing started'})

    @action(detail=True, methods=['post'], url_path='stop-screen-share')
    def stop_screen_share(self, request, pk=None):
        """Mark that the authenticated user stopped screen sharing."""
        meeting = self.get_object()
        state, _ = ParticipantState.objects.get_or_create(
            meeting=meeting, user=request.user
        )
        state.screen_sharing = False
        state.save()
        return Response({'message': 'Screen sharing stopped'})


#  إدارة رسائل الاجتماع
class MessageListCreateView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        meeting_id = self.kwargs.get('meeting_id')
        meeting = Meeting.objects.get(id=meeting_id)

        if self.request.user != meeting.user and self.request.user.role != 'admin':
            raise PermissionDenied("You are not allowed to view messages for this meeting.")

        return Message.objects.filter(meeting=meeting).order_by('timestamp')

    def perform_create(self, serializer):
        meeting_id = self.kwargs.get('meeting_id')
        meeting = Meeting.objects.get(id=meeting_id)

        if self.request.user != meeting.user and self.request.user.role != 'admin':
            raise PermissionDenied("You are not allowed to send messages to this meeting.")

        serializer.save(user=self.request.user, meeting=meeting)


#  إدارة إشارات WebRTC (Offer, Answer, ICE)
class SignalListCreateView(generics.ListCreateAPIView):
    serializer_class = SignalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        meeting_id = self.kwargs.get('meeting_id')
        meeting = Meeting.objects.get(id=meeting_id)

        if self.request.user != meeting.user and self.request.user.role != 'admin':
            raise PermissionDenied("Access denied to this meeting’s signaling.")

        return Signal.objects.filter(meeting=meeting).order_by('created_at')

    def perform_create(self, serializer):
        meeting_id = self.kwargs.get('meeting_id')
        meeting = Meeting.objects.get(id=meeting_id)

        if self.request.user != meeting.user and self.request.user.role != 'admin':
            raise PermissionDenied("You cannot send signaling to this meeting.")

        serializer.save(sender=self.request.user, meeting=meeting)

class RecordingListCreateView(generics.ListCreateAPIView):
    serializer_class = RecordingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        meeting_id = self.kwargs.get('meeting_id')
        meeting = Meeting.objects.get(id=meeting_id)

        if self.request.user != meeting.user and self.request.user.role != 'admin':
            raise PermissionDenied("You cannot view recordings for this meeting.")

        return Recording.objects.filter(meeting=meeting).order_by('-created_at')

    def perform_create(self, serializer):
        meeting_id = self.kwargs.get('meeting_id')
        meeting = Meeting.objects.get(id=meeting_id)

        if self.request.user != meeting.user and self.request.user.role != 'admin':
            raise PermissionDenied("You cannot upload a recording for this meeting.")

        serializer.save(uploaded_by=self.request.user, meeting=meeting)

#  الاجتماعات القادمة
class UpcomingMeetingsView(generics.ListAPIView):
    serializer_class = MeetingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        now = timezone.now()

        if user.role == 'admin':
            return Meeting.objects.filter(scheduled_date__gt=now).order_by('scheduled_date')
        return Meeting.objects.filter(user=user, scheduled_date__gt=now).order_by('scheduled_date')


#  الاجتماعات السابقة أو المنتهية
class PreviousMeetingsView(generics.ListAPIView):
    serializer_class = MeetingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        now = timezone.now()

        if user.role == 'admin':
            return Meeting.objects.filter(scheduled_date__lte=now).order_by('-scheduled_date')
        return Meeting.objects.filter(user=user, scheduled_date__lte=now).order_by('-scheduled_date')

class UserDashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        meetings = Meeting.objects.filter(user=user)
        meetings_data = MeetingSerializer(meetings, many=True).data

        total_meetings = meetings.count()
        total_recordings = sum([meeting.recordings.count() for meeting in meetings])
        total_messages = sum([meeting.messages.count() for meeting in meetings])

        return Response({
            "user_email": user.email,
            "full_name": getattr(user, 'full_name', ''),
            "total_meetings": total_meetings,
            "total_recordings": total_recordings,
            "total_messages": total_messages,
            "meetings": meetings_data,
        })
