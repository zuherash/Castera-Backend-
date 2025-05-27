from rest_framework import viewsets, permissions
from .models import Meeting
from .serializers import MeetingSerializer
from .permissions import IsOwnerOrAdmin

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
