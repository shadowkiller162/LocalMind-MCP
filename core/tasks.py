# core/tasks.py
import time

from celery import shared_task
from django.utils import timezone

from .models import Conversation
from .models import Message


@shared_task(bind=True, max_retries=3)
def process_ai_reply(self, message_id):
    """處理 AI 回覆的 Celery 任務"""

    try:
        # 獲取使用者訊息
        user_message = Message.objects.get(id=message_id)
        conversation = user_message.conversation

        # 記錄開始時間
        start_time = time.time()

        # 獲取對話上下文
        context_messages = conversation.get_context_messages(limit=10)

        # 建構 AI 請求的上下文
        context = []
        for msg in reversed(context_messages):
            role = "user" if msg.is_from_user else "assistant"
            context.append({
                "role": role,
                "content": msg.content,
            })

        # 呼叫 AI 服務 (目前使用模擬回覆)
        ai_response = generate_ai_response(context, user_message.content)

        # 計算處理時間
        processing_time = time.time() - start_time

        # 建立 AI 回覆訊息
        ai_message = Message.objects.create(
            conversation=conversation,
            sender=Message.SenderType.AI,
            content=ai_response,
            is_processed=True,
            processing_time=processing_time,
        )

        # 標記使用者訊息為已處理
        user_message.mark_as_processed(processing_time)

        # 更新對話的最後更新時間
        conversation.updated_at = timezone.now()
        conversation.save(update_fields=["updated_at"])

        return {
            "success": True,
            "user_message_id": user_message.id,
            "ai_message_id": ai_message.id,
            "processing_time": processing_time,
        }

    except Message.DoesNotExist:
        return {
            "success": False,
            "error": f"Message with id {message_id} not found",
        }
    except Exception as exc:
        # 重試機制
        if self.request.retries < self.max_retries:
            # 延遲重試 (指數退避)
            countdown = 2 ** self.request.retries
            raise self.retry(exc=exc, countdown=countdown)

        # 重試次數用完，記錄錯誤
        return {
            "success": False,
            "error": str(exc),
            "retries_exhausted": True,
        }


def generate_ai_response(context, user_message):
    """
    生成 AI 回覆 - 整合真實 AI 服務

    Args:
        context: 對話上下文列表
        user_message: 使用者訊息內容

    Returns:
        AI 回覆內容
    """
    import logging

    from .services.factory import AIServiceFactory

    logger = logging.getLogger(__name__)

    try:
        # 建立 AI 服務實例
        ai_service = AIServiceFactory.create_service()

        # 準備訊息格式
        messages = []

        # 添加系統訊息
        messages.append({
            "role": "system",
            "content": "你是一個友善、專業的 AI 助手。請用繁體中文回答問題，提供有用且準確的資訊。",
        })

        # 添加對話上下文
        if context:
            for msg in context:
                role = "user" if msg.get("is_from_user") else "assistant"
                messages.append({
                    "role": role,
                    "content": msg.get("content", ""),
                })

        # 添加當前使用者訊息
        messages.append({
            "role": "user",
            "content": user_message,
        })

        # 呼叫 AI 服務
        logger.info(f"使用 {ai_service.get_service_name()} 服務生成回覆")
        response = ai_service.generate_response(messages)

        if response.is_success:
            logger.info(f"AI 回覆成功生成，內容長度：{len(response.content)}")
            return response.content
        else:
            logger.error(f"AI 服務錯誤：{response.error}")
            # 回退到簡單回覆
            return f"抱歉，我目前無法處理您的請求。錯誤：{response.error}"

    except Exception as e:
        logger.error(f"生成 AI 回覆時發生錯誤：{e!s}", exc_info=True)
        # 回退到簡單回覆
        return f"我理解您提到的內容：「{user_message}」。作為 AI 助手，我會盡力協助您。請告訴我您需要什麼具體的幫助？"


@shared_task
def cleanup_old_conversations():
    """清理舊的對話數據 (定期任務)"""

    from datetime import timedelta

    from django.utils import timezone

    # 刪除 30 天前的非活躍對話
    cutoff_date = timezone.now() - timedelta(days=30)

    old_conversations = Conversation.objects.filter(
        updated_at__lt=cutoff_date,
        is_active=False,
    )

    deleted_count = old_conversations.count()
    old_conversations.delete()

    return {
        "success": True,
        "deleted_conversations": deleted_count,
        "cutoff_date": cutoff_date.isoformat(),
    }
