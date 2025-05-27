from rest_framework import viewsets, permissions
from .models import Meeting
from .serializers import MeetingSerializer
from .permissions import IsOwnerOrAdmin
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def join_meeting(request, room_id):
    try:
        meeting = Meeting.objects.get(room_id=room_id)
    except Meeting.DoesNotExist:
        return Response({'error': 'Meeting not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = MeetingSerializer(meeting)
    return Response(serializer.data)
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
