# core/api/ai_views.py

from drf_spectacular.openapi import OpenApiParameter
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..services.factory import AIServiceFactory


@extend_schema(
    summary="測試 AI 服務狀態",
    description="檢查所有 AI 服務的可用狀態",
    responses={200: {
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "data": {
                "type": "object",
                "properties": {
                    "services": {
                        "type": "object",
                        "additionalProperties": {"type": "boolean"},
                    },
                    "default_service": {"type": "string"},
                },
            },
        },
    }},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def ai_service_status(request):
    """檢查 AI 服務狀態"""
    try:
        # 取得所有服務的可用狀態
        services_status = AIServiceFactory.get_available_services()

        # 取得預設服務
        default_service = AIServiceFactory.create_service()

        return Response({
            "success": True,
            "data": {
                "services": services_status,
                "default_service": default_service.get_service_name(),
                "default_service_available": default_service.is_available(),
            },
        })
    except Exception as e:
        return Response({
            "success": False,
            "error": str(e),
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    summary="測試 AI 回覆生成",
    description="直接測試 AI 服務的回覆生成功能",
    parameters=[
        OpenApiParameter(
            name="service",
            description="指定使用的 AI 服務 (openai, anthropic, google, mock)",
            required=False,
            type=str,
            location=OpenApiParameter.QUERY,
        ),
    ],
    request={
        "type": "object",
        "properties": {
            "message": {"type": "string", "description": "測試訊息"},
            "context": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "role": {"type": "string", "enum": ["user", "assistant"]},
                        "content": {"type": "string"},
                    },
                },
                "description": "對話上下文（可選）",
            },
        },
        "required": ["message"],
    },
    responses={200: {
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "data": {
                "type": "object",
                "properties": {
                    "service_name": {"type": "string"},
                    "response": {"type": "string"},
                    "model": {"type": "string"},
                    "tokens_used": {"type": "integer", "nullable": True},
                    "finish_reason": {"type": "string", "nullable": True},
                },
            },
        },
    }},
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def test_ai_response(request):
    """測試 AI 回覆生成"""
    try:
        # 取得請求參數
        message = request.data.get("message")
        context = request.data.get("context", [])
        service_name = request.query_params.get("service")

        if not message:
            return Response({
                "success": False,
                "error": "message 欄位為必填",
            }, status=status.HTTP_400_BAD_REQUEST)

        # 建立 AI 服務
        ai_service = AIServiceFactory.create_service(service_name)

        # 準備訊息格式
        messages = []

        # 添加上下文
        for ctx in context:
            if isinstance(ctx, dict) and "role" in ctx and "content" in ctx:
                messages.append(ctx)

        # 添加當前訊息
        messages.append({
            "role": "user",
            "content": message,
        })

        # 生成回覆
        response = ai_service.generate_response(messages)

        if response.is_success:
            return Response({
                "success": True,
                "data": {
                    "service_name": ai_service.get_service_name(),
                    "response": response.content,
                    "model": response.model,
                    "tokens_used": response.tokens_used,
                    "finish_reason": response.finish_reason,
                    "metadata": response.metadata,
                },
            })
        else:
            return Response({
                "success": False,
                "error": response.error,
                "service_name": ai_service.get_service_name(),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        return Response({
            "success": False,
            "error": str(e),
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
