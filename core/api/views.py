# core/api/views.py
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter
from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models import Conversation
from core.models import Message

from .serializers import ConversationCreateSerializer
from .serializers import ConversationDetailSerializer
from .serializers import ConversationListSerializer
from .serializers import MessageCreateSerializer
from .serializers import MessageSerializer


class ConversationListCreateView(generics.ListCreateAPIView):
    """對話列表與建立 API"""

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """只返回當前使用者的對話"""
        return Conversation.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        """根據請求方法選擇序列化器"""
        if self.request.method == "POST":
            return ConversationCreateSerializer
        return ConversationListSerializer

    @extend_schema(
        summary="獲取對話列表",
        description="獲取當前使用者的所有對話列表",
        responses={200: ConversationListSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        """獲取對話列表"""
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="建立新對話",
        description="為當前使用者建立新的對話",
        request=ConversationCreateSerializer,
        responses={201: ConversationDetailSerializer},
    )
    def post(self, request, *args, **kwargs):
        """建立新對話"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        conversation = serializer.save()

        # 返回詳細信息
        detail_serializer = ConversationDetailSerializer(conversation)
        return Response(
            {
                "success": True,
                "message": "對話建立成功",
                "data": detail_serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )


class ConversationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """對話詳情 API"""

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """只返回當前使用者的對話"""
        return Conversation.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        """根據請求方法選擇序列化器"""
        if self.request.method in ["PUT", "PATCH"]:
            return ConversationCreateSerializer
        return ConversationDetailSerializer

    @extend_schema(
        summary="獲取對話詳情",
        description="獲取特定對話的詳細資訊，包含所有訊息",
        responses={200: ConversationDetailSerializer},
    )
    def get(self, request, *args, **kwargs):
        """獲取對話詳情"""
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="更新對話",
        description="更新對話標題或狀態",
        request=ConversationCreateSerializer,
        responses={200: ConversationDetailSerializer},
    )
    def patch(self, request, *args, **kwargs):
        """更新對話"""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        conversation = serializer.save()

        # 返回詳細信息
        detail_serializer = ConversationDetailSerializer(conversation)
        return Response(
            {
                "success": True,
                "message": "對話更新成功",
                "data": detail_serializer.data,
            },
        )

    @extend_schema(
        summary="刪除對話",
        description="刪除特定對話及其所有訊息",
        responses={204: None},
    )
    def delete(self, request, *args, **kwargs):
        """刪除對話"""
        return super().delete(request, *args, **kwargs)


class MessageListCreateView(generics.ListCreateAPIView):
    """訊息列表與建立 API"""

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """獲取特定對話的訊息"""
        conversation_id = self.kwargs.get("conversation_id")
        conversation = get_object_or_404(
            Conversation,
            id=conversation_id,
            user=self.request.user,
        )
        return Message.objects.filter(conversation=conversation)

    def get_serializer_class(self):
        """根據請求方法選擇序列化器"""
        if self.request.method == "POST":
            return MessageCreateSerializer
        return MessageSerializer

    @extend_schema(
        summary="獲取訊息列表",
        description="獲取特定對話的所有訊息",
        parameters=[
            OpenApiParameter(
                name="conversation_id",
                description="對話ID",
                required=True,
                type=int,
                location=OpenApiParameter.PATH,
            ),
        ],
        responses={200: MessageSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        """獲取訊息列表"""
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="發送訊息",
        description="向特定對話發送新訊息，將觸發AI回覆處理",
        parameters=[
            OpenApiParameter(
                name="conversation_id",
                description="對話ID",
                required=True,
                type=int,
                location=OpenApiParameter.PATH,
            ),
        ],
        request=MessageCreateSerializer,
        responses={201: MessageSerializer},
    )
    def post(self, request, *args, **kwargs):
        """發送訊息"""
        # 驗證對話存在
        conversation_id = self.kwargs.get("conversation_id")
        conversation = get_object_or_404(
            Conversation,
            id=conversation_id,
            user=self.request.user,
        )

        # 建立訊息
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        message = serializer.save(conversation=conversation)

        # 觸發AI回覆處理
        from core.tasks import process_ai_reply
        process_ai_reply.delay(message.id)

        return Response(
            {
                "success": True,
                "message": "訊息發送成功",
                "data": MessageSerializer(message).data,
            },
            status=status.HTTP_201_CREATED,
        )


@extend_schema(
    summary="獲取對話上下文",
    description="獲取對話的上下文訊息，用於AI處理",
    parameters=[
        OpenApiParameter(
            name="conversation_id",
            description="對話ID",
            required=True,
            type=int,
            location=OpenApiParameter.PATH,
        ),
        OpenApiParameter(
            name="limit",
            description="返回訊息數量限制",
            required=False,
            type=int,
            location=OpenApiParameter.QUERY,
        ),
    ],
    responses={200: MessageSerializer(many=True)},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_conversation_context(request, conversation_id):
    """獲取對話上下文"""
    conversation = get_object_or_404(
        Conversation,
        id=conversation_id,
        user=request.user,
    )

    limit = int(request.query_params.get("limit", 10))
    context_messages = conversation.get_context_messages(limit=limit)

    serializer = MessageSerializer(context_messages, many=True)

    return Response(
        {
            "success": True,
            "data": {
                "conversation_id": conversation.id,
                "conversation_title": conversation.title,
                "context_messages": serializer.data,
            },
        },
    )
