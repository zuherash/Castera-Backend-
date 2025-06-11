from django.contrib import admin
from .models import Meeting, Message, Signal, Recording


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "type_of", "scheduled_date", "status")
    search_fields = ("title", "user__email", "room_id")
    list_filter = ("status", "type_of")
    readonly_fields = ("room_id", "created_on")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("meeting", "user", "timestamp")
    search_fields = ("meeting__title", "user__email", "content")


@admin.register(Signal)
class SignalAdmin(admin.ModelAdmin):
    list_display = ("meeting", "sender", "signal_type", "created_at")
    search_fields = ("meeting__title", "sender__email")
    list_filter = ("signal_type",)


@admin.register(Recording)
class RecordingAdmin(admin.ModelAdmin):
    list_display = ("meeting", "uploaded_by", "created_at")
    search_fields = ("meeting__title", "uploaded_by__email")
