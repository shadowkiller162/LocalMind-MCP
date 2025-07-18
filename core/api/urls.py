# core/api/urls.py
from django.urls import path

from . import ai_views
from . import views

app_name = "core_api"

urlpatterns = [
    # 對話相關 API
    path(
        "conversations/",
        views.ConversationListCreateView.as_view(),
        name="conversation-list-create",
    ),
    path(
        "conversations/<int:pk>/",
        views.ConversationDetailView.as_view(),
        name="conversation-detail",
    ),
    path(
        "conversations/<int:conversation_id>/context/",
        views.get_conversation_context,
        name="conversation-context",
    ),

    # 訊息相關 API
    path(
        "conversations/<int:conversation_id>/messages/",
        views.MessageListCreateView.as_view(),
        name="message-list-create",
    ),

    # AI 服務測試 API
    path(
        "ai/status/",
        ai_views.ai_service_status,
        name="ai-service-status",
    ),
    path(
        "ai/test/",
        ai_views.test_ai_response,
        name="test-ai-response",
    ),
]
