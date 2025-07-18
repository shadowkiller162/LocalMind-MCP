from django.conf import settings
from django.db import models


class Conversation(models.Model):
    """對話模型 - 管理使用者與AI的對話會話"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="conversations",
        verbose_name="使用者",
    )
    title = models.CharField(max_length=255, verbose_name="對話標題")
    is_active = models.BooleanField(default=True, verbose_name="是否啟用")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    class Meta:
        ordering = ["-updated_at"]
        verbose_name = "對話"
        verbose_name_plural = "對話"

    def __str__(self):
        return f"{self.user.email} - {self.title}"

    @property
    def message_count(self):
        """獲取對話中的訊息數量"""
        return self.messages.count()

    @property
    def last_message(self):
        """獲取最後一條訊息"""
        return self.messages.order_by("-timestamp").first()

    def get_context_messages(self, limit=10):
        """獲取對話上下文訊息 (最近的N條訊息，按時間正序排列)"""
        # 先取最近的N條訊息，轉為list後再排序
        recent_messages = list(self.messages.order_by("-timestamp")[:limit])
        return sorted(recent_messages, key=lambda msg: msg.timestamp)


class Message(models.Model):
    """訊息模型 - 存放對話中的每條訊息"""

    class SenderType(models.TextChoices):
        USER = "user", "使用者"
        AI = "ai", "AI助手"

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
        verbose_name="對話",
    )
    sender = models.CharField(
        max_length=50,
        choices=SenderType.choices,
        verbose_name="發送者",
    )
    content = models.TextField(verbose_name="訊息內容")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="發送時間")
    is_processed = models.BooleanField(default=False, verbose_name="是否已處理")
    processing_time = models.FloatField(
        null=True, blank=True, verbose_name="處理時間(秒)",
    )

    class Meta:
        ordering = ["timestamp"]
        verbose_name = "訊息"
        verbose_name_plural = "訊息"

    def __str__(self):
        return f"{self.get_sender_display()}: {self.content[:30]}"

    def mark_as_processed(self, processing_time=None):
        """標記訊息為已處理"""
        self.is_processed = True
        if processing_time:
            self.processing_time = processing_time
        self.save(update_fields=["is_processed", "processing_time"])

    @property
    def is_from_user(self):
        """判斷是否為使用者發送的訊息"""
        return self.sender == self.SenderType.USER

    @property
    def is_from_ai(self):
        """判斷是否為AI發送的訊息"""
        return self.sender == self.SenderType.AI
