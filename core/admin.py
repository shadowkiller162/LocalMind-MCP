from django.contrib import admin

from .models import Conversation
from .models import Message


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "title", "updated_at")
    search_fields = ("title", "user__email")
    ordering = ("-updated_at",)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "conversation", "sender", "content", "timestamp")
    list_filter = ("sender",)
    search_fields = ("content",)
    ordering = ("-timestamp",)
