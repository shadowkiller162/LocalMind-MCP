# core/services/ai_service.py
import logging
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class AIResponse:
    """AI 回覆回應資料結構"""
    content: str
    model: str
    tokens_used: int | None = None
    finish_reason: str | None = None
    error: str | None = None
    metadata: dict[str, Any] | None = None

    @property
    def is_success(self) -> bool:
        """檢查回應是否成功"""
        return self.error is None and bool(self.content.strip())


class AIService(ABC):
    """AI 服務抽象基類"""

    def __init__(self, config: dict[str, Any]):
        """
        初始化 AI 服務

        Args:
            config: 服務配置字典
        """
        self.config = config
        self.api_key = config.get("API_KEY", "")
        self.model = config.get("MODEL", "")
        self.max_tokens = config.get("MAX_TOKENS", 1000)
        self.temperature = config.get("TEMPERATURE", 0.7)
        self.timeout = config.get("TIMEOUT", 30)
        self.enabled = config.get("ENABLED", False)

        # 驗證必要配置
        if not self.api_key and self.enabled:
            logger.warning(f"{self.__class__.__name__}: API_KEY 未設置，服務將被禁用")
            self.enabled = False

    @abstractmethod
    def generate_response(
        self,
        messages: list[dict[str, str]],
        **kwargs,
    ) -> AIResponse:
        """
        生成 AI 回覆

        Args:
            messages: 對話訊息列表，格式為 [{"role": "user/assistant", "content": "..."}]
            **kwargs: 額外參數

        Returns:
            AIResponse: AI 回覆物件
        """

    @abstractmethod
    def get_service_name(self) -> str:
        """取得服務名稱"""

    def is_available(self) -> bool:
        """檢查服務是否可用"""
        return self.enabled and bool(self.api_key)

    def validate_messages(self, messages: list[dict[str, str]]) -> bool:
        """
        驗證訊息格式

        Args:
            messages: 訊息列表

        Returns:
            bool: 是否有效
        """
        if not messages:
            return False

        for message in messages:
            if not isinstance(message, dict):
                return False
            if "role" not in message or "content" not in message:
                return False
            if message["role"] not in ["user", "assistant", "system"]:
                return False
            if not isinstance(message["content"], str) or not message["content"].strip():
                return False

        return True

    def format_error_response(self, error: str, model: str = None) -> AIResponse:
        """
        格式化錯誤回應

        Args:
            error: 錯誤訊息
            model: 模型名稱

        Returns:
            AIResponse: 錯誤回應物件
        """
        return AIResponse(
            content="",
            model=model or self.model,
            error=error,
        )

    def log_request(self, messages: list[dict[str, str]]) -> None:
        """記錄請求日誌"""
        logger.info(
            f"{self.get_service_name()} 請求: "
            f"模型={self.model}, "
            f"訊息數量={len(messages)}, "
            f"最大token={self.max_tokens}",
        )

    def log_response(self, response: AIResponse) -> None:
        """記錄回應日誌"""
        if response.is_success:
            logger.info(
                f"{self.get_service_name()} 成功回應: "
                f"內容長度={len(response.content)}, "
                f"使用token={response.tokens_used}",
            )
        else:
            logger.error(
                f"{self.get_service_name()} 錯誤回應: "
                f"{response.error}",
            )
