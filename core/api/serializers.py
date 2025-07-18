# core/api/serializers.py
from rest_framework import serializers

from core.models import Conversation
from core.models import Message


class MessageSerializer(serializers.ModelSerializer):
    """訊息序列化器"""

    sender_display = serializers.CharField(source="get_sender_display", read_only=True)
    is_from_user = serializers.BooleanField(read_only=True)
    is_from_ai = serializers.BooleanField(read_only=True)

    class Meta:
        model = Message
        fields = [
            "id", "conversation", "sender", "sender_display",
            "content", "timestamp", "is_processed", "processing_time",
            "is_from_user", "is_from_ai",
        ]
        read_only_fields = ["id", "timestamp", "is_processed", "processing_time"]

    def validate_content(self, value):
        """驗證訊息內容"""
        if not value or not value.strip():
            msg = "訊息內容不能為空"
            raise serializers.ValidationError(msg)

        max_content_length = 10000
        if len(value) > max_content_length:
            msg = "訊息內容不能超過10000字元"
            raise serializers.ValidationError(msg)

        return value.strip()


class ConversationListSerializer(serializers.ModelSerializer):
    """對話列表序列化器"""

    message_count = serializers.IntegerField(read_only=True)
    last_message = MessageSerializer(read_only=True)

    class Meta:
        model = Conversation
        fields = [
            "id", "title", "is_active", "created_at", "updated_at",
            "message_count", "last_message",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ConversationDetailSerializer(serializers.ModelSerializer):
    """對話詳情序列化器"""

    messages = MessageSerializer(many=True, read_only=True)
    message_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Conversation
        fields = [
            "id", "title", "is_active", "created_at", "updated_at",
            "message_count", "messages",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ConversationCreateSerializer(serializers.ModelSerializer):
    """建立對話序列化器"""

    class Meta:
        model = Conversation
        fields = ["title"]

    def validate_title(self, value):
        """驗證對話標題"""
        if not value or not value.strip():
            msg = "對話標題不能為空"
            raise serializers.ValidationError(msg)

        max_title_length = 255
        if len(value) > max_title_length:
            msg = "對話標題不能超過255字元"
            raise serializers.ValidationError(msg)

        return value.strip()

    def create(self, validated_data):
        """建立對話時自動設定使用者"""
        user = self.context["request"].user
        validated_data["user"] = user
        return super().create(validated_data)


class MessageCreateSerializer(serializers.ModelSerializer):
    """建立訊息序列化器"""

    class Meta:
        model = Message
        fields = ["content"]


    def validate_content(self, value):
        """驗證訊息內容"""
        if not value or not value.strip():
            msg = "訊息內容不能為空"
            raise serializers.ValidationError(msg)

        max_content_length = 10000
        if len(value) > max_content_length:
            msg = "訊息內容不能超過10000字元"
            raise serializers.ValidationError(msg)

        return value.strip()

    def create(self, validated_data):
        """建立訊息時自動設定發送者為使用者"""
        validated_data["sender"] = Message.SenderType.USER
        return super().create(validated_data)
