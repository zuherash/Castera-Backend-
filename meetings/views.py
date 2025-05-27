from rest_framework import viewsets, permissions, generics, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from .models import Meeting, Message, Signal
from .serializers import MeetingSerializer, MessageSerializer, SignalSerializer
from .permissions import IsOwnerOrAdmin


# ✅ الانضمام إلى اجتماع عبر room_id (UUID)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def join_meeting(request, room_id):
    try:
        meeting = Meeting.objects.get(room_id=room_id)
    except Meeting.DoesNotExist:
        return Response({'error': 'Meeting not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = MeetingSerializer(meeting)
    return Response(serializer.data)


# ✅ إدارة الاجتماعات
class MeetingViewSet(viewsets.ModelViewSet):
    serializer_class = MeetingSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Meeting.objects.all().order_by('-created_on')
        return Meeting.objects.filter(user=user).order_by('-created_on')

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


# ✅ إدارة رسائل الاجتماع
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


# ✅ إدارة إشارات WebRTC (Offer, Answer, ICE)
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
