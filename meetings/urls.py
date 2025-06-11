from django.urls import path
from .views import    SignalListCreateView, MeetingViewSet, join_meeting , MessageListCreateView , RecordingListCreateView , UpcomingMeetingsView,UserDashboardView , PreviousMeetingsView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'meetings', MeetingViewSet, basename='meeting')

urlpatterns = router.urls + [
    path('join/<uuid:room_id>/', join_meeting, name='join-meeting'),
    path('meetings/<int:meeting_id>/messages/', MessageListCreateView.as_view(), name='meeting-messages'),
    path('meetings/<int:meeting_id>/recordings/', RecordingListCreateView.as_view(), name='meeting-recordings'),
    path('meetings/upcoming/', UpcomingMeetingsView.as_view(), name='upcoming-meetings'),
    path('meetings/previous/', PreviousMeetingsView.as_view(), name='previous-meetings'),
    path('dashboard/', UserDashboardView.as_view(), name='user-dashboard'),
]
