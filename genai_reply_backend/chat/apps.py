from django.apps import AppConfig


class ChatConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "genai_reply_backend.chat"
    verbose_name = "Chat Interface"
