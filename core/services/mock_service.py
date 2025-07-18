# core/services/mock_service.py
import logging
import random
import time
from typing import Any

from .ai_service import AIResponse
from .ai_service import AIService

logger = logging.getLogger(__name__)


class MockAIService(AIService):
    """模擬 AI 服務實作（用於測試和開發）"""

    def __init__(self, config: dict[str, Any]):
        # Mock 服務總是可用的
        super().__init__(config)
        self.enabled = True
        self.api_key = "mock-api-key"
        self.model = config.get("MODEL", "mock-model")

    def get_service_name(self) -> str:
        return "Mock"

    def is_available(self) -> bool:
        """Mock 服務總是可用"""
        return True

    def generate_response(
        self,
        messages: list[dict[str, str]],
        **kwargs,
    ) -> AIResponse:
        """
        生成模擬 AI 回覆

        Args:
            messages: 對話訊息列表
            **kwargs: 額外參數

        Returns:
            AIResponse: AI 回覆物件
        """
        try:
            # 驗證訊息格式
            if not self.validate_messages(messages):
                return self.format_error_response("無效的訊息格式")

            self.log_request(messages)

            # 模擬處理時間
            processing_time = random.uniform(0.5, 2.0)
            time.sleep(processing_time)

            # 取得最後一則使用者訊息
            user_message = ""
            for message in reversed(messages):
                if message["role"] == "user":
                    user_message = message["content"]
                    break

            # 生成模擬回覆
            mock_content = self._generate_mock_response(user_message, messages)

            # 模擬 token 使用量
            estimated_tokens = len(mock_content) // 3 + random.randint(10, 50)

            ai_response = AIResponse(
                content=mock_content,
                model=self.model,
                tokens_used=estimated_tokens,
                finish_reason="stop",
                metadata={
                    "processing_time": processing_time,
                    "mock_service": True,
                    "conversation_length": len(messages),
                },
            )

            self.log_response(ai_response)
            return ai_response

        except Exception as e:
            error_msg = f"Mock 服務錯誤：{e!s}"
            logger.error(error_msg, exc_info=True)
            return self.format_error_response(error_msg)

    def _generate_mock_response(self, user_message: str, messages: list[dict[str, str]]) -> str:
        """
        生成模擬回覆內容

        Args:
            user_message: 使用者訊息
            messages: 完整對話歷史

        Returns:
            str: 模擬回覆內容
        """
        user_lower = user_message.lower()

        # 問候語回覆
        if any(greeting in user_lower for greeting in ["你好", "hello", "hi", "嗨"]):
            responses = [
                "您好！我是 AI 助手，很高興為您服務。請問有什麼可以幫助您的嗎？",
                "嗨！歡迎使用 MaiAgent，我是您的專屬 AI 助理。",
                "Hello! 我是 AI 助手，準備好協助您了。有什麼問題嗎？",
            ]
            return random.choice(responses)

        # 感謝語回覆
        elif any(thanks in user_lower for thanks in ["謝謝", "thank", "感謝"]):
            responses = [
                "不客氣！如果還有其他問題，隨時都可以問我。",
                "很高興能幫助您！有其他需要協助的地方嗎？",
                "我的榮幸！期待繼續為您服務。",
            ]
            return random.choice(responses)

        # 告別語回覆
        elif any(goodbye in user_lower for goodbye in ["再見", "bye", "goodbye", "掰掰"]):
            responses = [
                "再見！期待下次為您服務。",
                "掰掰！祝您有美好的一天。",
                "再會！如果之後有需要，隨時回來找我。",
            ]
            return random.choice(responses)

        # 問句回覆
        elif "?" in user_message or "？" in user_message:
            if "什麼" in user_message or "what" in user_lower:
                return f"關於「{user_message.replace('?', '').replace('？', '')}」這個問題，這是一個很有趣的主題。讓我為您詳細說明..."
            elif "怎麼" in user_message or "how" in user_lower:
                return f"要回答您的問題「{user_message}」，我建議您可以從以下幾個方面來考慮..."
            elif "為什麼" in user_message or "why" in user_lower:
                return f"您問「{user_message}」是個深入的問題。原因可能包括多個方面..."
            else:
                return f"關於您的問題「{user_message}」，我正在思考最佳的回答方式。請稍等片刻，我會提供詳細的回覆。"

        # 技術相關
        elif any(tech in user_lower for tech in ["程式", "程序", "code", "python", "django", "api"]):
            return f"我理解您對技術的詢問。關於「{user_message}」，這涉及到程式設計的概念。讓我為您解釋相關的技術細節..."

        # AI 相關
        elif any(ai in user_lower for ai in ["ai", "人工智慧", "機器學習", "深度學習"]):
            return f"關於人工智慧的話題「{user_message}」，這是一個非常前沿的領域。AI 技術正在快速發展，包括自然語言處理、機器學習等方面..."

        # 預設回覆
        else:
            responses = [
                f"我理解您提到的內容：「{user_message}」。作為 AI 助手，我會盡力協助您。請告訴我您需要什麼具體的幫助？",
                f"感謝您的訊息。關於「{user_message}」，我需要更多資訊才能提供最佳的回答。您能進一步說明嗎？",
                f"我注意到您提到了「{user_message}」。這是個有趣的話題，我很樂意與您深入討論。",
                f"您的訊息「{user_message}」很有意思。讓我想想如何最好地回應您。",
            ]
            return random.choice(responses)

    def get_available_models(self) -> list[str]:
        """取得可用的模擬模型列表"""
        return ["mock-model", "mock-gpt", "mock-claude", "mock-gemini"]
