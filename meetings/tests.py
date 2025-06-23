from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from users.models import User
from .models import Meeting, Message, Recording, ParticipantState


class APITests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="user@example.com")
        self.admin = User.objects.create_user(email="admin@example.com", role="admin")
        self.future_date = timezone.now() + timezone.timedelta(days=1)
        self.past_date = timezone.now() - timezone.timedelta(days=1)

        self.meeting_future = Meeting.objects.create(
            user=self.user,
            title="Future Meeting",
            description="test",
            scheduled_date=self.future_date,
        )

        self.meeting_past = Meeting.objects.create(
            user=self.user,
            title="Past Meeting",
            description="test",
            scheduled_date=self.past_date,
        )

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def test_join_meeting(self):
        self.authenticate(self.user)
        url = reverse("join-meeting", args=[self.meeting_future.room_id])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["id"], self.meeting_future.id)

    def test_meeting_crud_and_status(self):
        self.authenticate(self.user)
        url = reverse("meeting-list")
        data = {
            "title": "New meeting",
            "description": "desc",
            "scheduled_date": (timezone.now() + timezone.timedelta(days=2)).isoformat(),
        }
        resp = self.client.post(url, data, format="json")
        self.assertEqual(resp.status_code, 201)
        meeting_id = resp.data["id"]

        detail_url = reverse("meeting-detail", args=[meeting_id])
        resp = self.client.get(detail_url)
        self.assertEqual(resp.status_code, 200)

        resp = self.client.patch(detail_url, {"title": "Updated"}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["title"], "Updated")

        status_url = reverse("meeting-set-status", args=[meeting_id])
        resp = self.client.post(status_url, {"status": "ended"}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["message"], "Status set to ended")

    def test_messages_endpoint(self):
        self.authenticate(self.user)
        url = reverse("meeting-messages", args=[self.meeting_future.id])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data, [])

        data = {"content": "hello", "meeting": self.meeting_future.id}
        resp = self.client.post(url, data, format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(Message.objects.count(), 1)

    def test_recordings_endpoint(self):
        self.authenticate(self.user)
        url = reverse("meeting-recordings", args=[self.meeting_future.id])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data, [])

        data = {"file_url": "http://example.com/video.mp4", "meeting": self.meeting_future.id}
        resp = self.client.post(url, data, format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(Recording.objects.count(), 1)

    def test_call_actions(self):
        self.authenticate(self.user)
        mute_url = reverse("meeting-mute-audio", args=[self.meeting_future.id])
        resp = self.client.post(mute_url)
        self.assertEqual(resp.status_code, 200)
        state = ParticipantState.objects.get(meeting=self.meeting_future, user=self.user)
        self.assertTrue(state.audio_muted)

        video_url = reverse("meeting-stop-video", args=[self.meeting_future.id])
        resp = self.client.post(video_url)
        self.assertEqual(resp.status_code, 200)
        state.refresh_from_db()
        self.assertTrue(state.video_stopped)

        stop_url = reverse("meeting-stop-call", args=[self.meeting_future.id])
        resp = self.client.post(stop_url)
        self.assertEqual(resp.status_code, 200)
        state.refresh_from_db()
        self.assertFalse(state.in_call)

    def test_upcoming_previous_dashboard(self):
        self.authenticate(self.user)
        upcoming_url = reverse("upcoming-meetings")
        resp = self.client.get(upcoming_url)
        self.assertEqual(len(resp.data), 1)

        previous_url = reverse("previous-meetings")
        resp = self.client.get(previous_url)
        self.assertEqual(len(resp.data), 1)

        dashboard_url = reverse("user-dashboard")
        resp = self.client.get(dashboard_url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["total_meetings"], 2)


class PermissionTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.owner = User.objects.create_user(email="owner@example.com")
        self.admin = User.objects.create_user(email="adm@example.com", role="admin")
        self.other = User.objects.create_user(email="other@example.com")
        self.meeting = Meeting.objects.create(
            user=self.owner,
            title="Test",
            description="desc",
            scheduled_date=timezone.now() + timezone.timedelta(days=1),
        )

    def test_owner_can_modify(self):
        self.client.force_authenticate(user=self.owner)
        url = reverse("meeting-detail", args=[self.meeting.id])
        resp = self.client.patch(url, {"title": "Updated"}, format="json")
        self.assertEqual(resp.status_code, 200)

    def test_admin_can_modify(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse("meeting-detail", args=[self.meeting.id])
        resp = self.client.patch(url, {"title": "Updated by admin"}, format="json")
        self.assertEqual(resp.status_code, 200)

    def test_other_cannot_modify_but_can_view(self):
        self.client.force_authenticate(user=self.other)
        url = reverse("meeting-detail", args=[self.meeting.id])
        resp = self.client.patch(url, {"title": "Hacker"}, format="json")
        self.assertEqual(resp.status_code, 403)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
