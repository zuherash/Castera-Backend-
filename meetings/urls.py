from django.urls import path
from .views import MeetingViewSet, join_meeting
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'meetings', MeetingViewSet, basename='meeting')

urlpatterns = router.urls + [
    path('join/<uuid:room_id>/', join_meeting, name='join-meeting'),
]
