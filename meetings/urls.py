from django.urls import path
from .views import MeetingViewSet, join_meeting , MessageListCreateView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'meetings', MeetingViewSet, basename='meeting')

urlpatterns = router.urls + [
    path('join/<uuid:room_id>/', join_meeting, name='join-meeting'),
     path('meetings/<int:meeting_id>/messages/', MessageListCreateView.as_view(), name='meeting-messages'),
]
