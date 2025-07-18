# core/tests/test_models.py
import pytest
from django.contrib.auth import get_user_model

from ..models import Message

User = get_user_model()


@pytest.mark.django_db()
class TestConversationModel:
    """對話模型測試"""

    def test_conversation_creation(self, conversation):
        """測試對話建立"""
        assert conversation.user is not None
        assert conversation.title != ""
        assert conversation.is_active is True
        assert conversation.created_at is not None
        assert conversation.updated_at is not None

    def test_conversation_str_representation(self, conversation):
        """測試對話字串表示"""
        expected = f"{conversation.user.email} - {conversation.title}"
        assert str(conversation) == expected

    def test_message_count_property(self, conversation):
        """測試訊息數量屬性"""
        # 初始應該為 0
        assert conversation.message_count == 0

        # 添加一條訊息
        Message.objects.create(
            conversation=conversation,
            sender=Message.SenderType.USER,
            content="測試訊息",
        )

        # 應該為 1
        assert conversation.message_count == 1

    def test_last_message_property(self, conversation):
        """測試最後一條訊息屬性"""
        # 初始應該為 None
        assert conversation.last_message is None

        # 添加訊息
        message1 = Message.objects.create(
            conversation=conversation,
            sender=Message.SenderType.USER,
            content="第一條訊息",
        )

        message2 = Message.objects.create(
            conversation=conversation,
            sender=Message.SenderType.AI,
            content="第二條訊息",
        )

        # 最後一條訊息應該是 message2
        assert conversation.last_message == message2

    def test_get_context_messages(self, conversation):
        """測試獲取上下文訊息"""
        # 創建多條訊息
        for i in range(5):
            Message.objects.create(
                conversation=conversation,
                sender=Message.SenderType.USER,
                content=f"訊息 {i}",
            )

        # 獲取最近3條訊息
        context = conversation.get_context_messages(limit=3)
        assert len(context) == 3

        # 應該是按時間倒序
        assert context[0].content == "訊息 4"
        assert context[1].content == "訊息 3"
        assert context[2].content == "訊息 2"


@pytest.mark.django_db()
class TestMessageModel:
    """訊息模型測試"""

    def test_message_creation(self, message):
        """測試訊息建立"""
        assert message.conversation is not None
        assert message.sender == Message.SenderType.USER
        assert message.content != ""
        assert message.is_processed is False
        assert message.processing_time is None
        assert message.timestamp is not None

    def test_message_str_representation(self, conversation):
        """測試訊息字串表示"""
        message = Message.objects.create(
            conversation=conversation,
            sender=Message.SenderType.AI,
            content="這是一條很長的測試訊息內容，用來測試字串表示方法",
        )

        expected = "AI助手: 這是一條很長的測試訊息內容，用來測試字串表示方法"
        assert str(message) == expected

    def test_mark_as_processed(self, message):
        """測試標記為已處理"""
        # 初始狀態
        assert message.is_processed is False
        assert message.processing_time is None

        # 標記為已處理
        message.mark_as_processed(processing_time=1.5)

        # 刷新數據
        message.refresh_from_db()

        assert message.is_processed is True
        assert message.processing_time == 1.5

    def test_sender_type_properties(self, conversation):
        """測試發送者類型屬性"""
        # 測試使用者訊息
        user_message = Message.objects.create(
            conversation=conversation,
            sender=Message.SenderType.USER,
            content="使用者訊息",
        )

        assert user_message.is_from_user is True
        assert user_message.is_from_ai is False

        # 測試AI訊息
        ai_message = Message.objects.create(
            conversation=conversation,
            sender=Message.SenderType.AI,
            content="AI訊息",
        )

        assert ai_message.is_from_user is False
        assert ai_message.is_from_ai is True

    def test_message_ordering(self, conversation):
        """測試訊息排序"""
        # 創建多條訊息
        message1 = Message.objects.create(
            conversation=conversation,
            sender=Message.SenderType.USER,
            content="第一條訊息",
        )

        message2 = Message.objects.create(
            conversation=conversation,
            sender=Message.SenderType.AI,
            content="第二條訊息",
        )

        # 獲取所有訊息
        messages = list(Message.objects.filter(conversation=conversation))

        # 應該按時間正序排列
        assert messages[0] == message1
        assert messages[1] == message2
