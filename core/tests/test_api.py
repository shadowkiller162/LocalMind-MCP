# core/tests/test_api.py
import pytest
from django.urls import reverse
from rest_framework import status

from ..models import Conversation
from ..models import Message


@pytest.mark.django_db()
class TestConversationAPI:
    """對話 API 測試"""

    def test_conversation_list(self, authenticated_client, conversation):
        """測試對話列表 API"""
        url = reverse("core_api:conversation-list-create")
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["title"] == conversation.title

    def test_conversation_create(self, authenticated_client):
        """測試建立對話 API"""
        url = reverse("core_api:conversation-list-create")
        data = {"title": "新對話"}

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["success"] is True
        assert response.data["data"]["title"] == "新對話"

        # 驗證數據庫中的對話
        assert Conversation.objects.count() == 1

    def test_conversation_create_invalid_title(self, authenticated_client):
        """測試建立對話時標題無效"""
        url = reverse("core_api:conversation-list-create")
        data = {"title": ""}

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_conversation_detail(self, authenticated_client, conversation):
        """測試對話詳情 API"""
        url = reverse("core_api:conversation-detail", kwargs={"pk": conversation.pk})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == conversation.title
        assert response.data["message_count"] == 0

    def test_conversation_update(self, authenticated_client, conversation):
        """測試更新對話 API"""
        url = reverse("core_api:conversation-detail", kwargs={"pk": conversation.pk})
        data = {"title": "更新的對話標題"}

        response = authenticated_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert response.data["data"]["title"] == "更新的對話標題"

        # 驗證數據庫中的對話
        conversation.refresh_from_db()
        assert conversation.title == "更新的對話標題"

    def test_conversation_delete(self, authenticated_client, conversation):
        """測試刪除對話 API"""
        url = reverse("core_api:conversation-detail", kwargs={"pk": conversation.pk})
        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # 驗證對話已被刪除
        assert not Conversation.objects.filter(pk=conversation.pk).exists()

    def test_conversation_access_control(self, authenticated_client, user):
        """測試對話訪問控制"""
        from .conftest import ConversationFactory
        from .conftest import UserFactory

        # 創建另一個使用者
        other_user = UserFactory()

        # 創建屬於其他使用者的對話
        other_conversation = ConversationFactory(user=other_user)

        # 嘗試訪問其他使用者的對話
        url = reverse("core_api:conversation-detail", kwargs={"pk": other_conversation.pk})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db()
class TestMessageAPI:
    """訊息 API 測試"""

    def test_message_list(self, authenticated_client, conversation, message):
        """測試訊息列表 API"""
        url = reverse("core_api:message-list-create", kwargs={"conversation_id": conversation.pk})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["content"] == message.content

    def test_message_create(self, authenticated_client, conversation):
        """測試發送訊息 API"""
        url = reverse("core_api:message-list-create", kwargs={"conversation_id": conversation.pk})
        data = {
            "conversation": conversation.pk,
            "content": "新的測試訊息",
        }

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["success"] is True
        assert response.data["data"]["content"] == "新的測試訊息"
        assert response.data["data"]["sender"] == Message.SenderType.USER

        # 驗證數據庫中的訊息
        assert Message.objects.count() == 1

    def test_message_create_invalid_content(self, authenticated_client, conversation):
        """測試發送空訊息"""
        url = reverse("core_api:message-list-create", kwargs={"conversation_id": conversation.pk})
        data = {
            "conversation": conversation.pk,
            "content": "",
        }

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_message_access_control(self, authenticated_client, user):
        """測試訊息訪問控制"""
        from .conftest import ConversationFactory
        from .conftest import UserFactory

        # 創建另一個使用者
        other_user = UserFactory()

        # 創建屬於其他使用者的對話
        other_conversation = ConversationFactory(user=other_user)

        # 嘗試訪問其他使用者的對話訊息
        url = reverse("core_api:message-list-create", kwargs={"conversation_id": other_conversation.pk})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_conversation_context_api(self, authenticated_client, conversation):
        """測試對話上下文 API"""
        # 創建多條訊息
        for i in range(5):
            Message.objects.create(
                conversation=conversation,
                sender=Message.SenderType.USER,
                content=f"訊息 {i}",
            )

        url = reverse("core_api:conversation-context", kwargs={"conversation_id": conversation.pk})
        response = authenticated_client.get(url, {"limit": 3})

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert len(response.data["data"]["context_messages"]) == 3
        assert response.data["data"]["conversation_title"] == conversation.title


@pytest.mark.django_db()
class TestAuthenticationAPI:
    """認證測試"""

    def test_unauthenticated_access(self, api_client):
        """測試未認證訪問"""
        url = reverse("core_api:conversation-list-create")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_authenticated_access(self, authenticated_client):
        """測試認證後訪問"""
        url = reverse("core_api:conversation-list-create")
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
