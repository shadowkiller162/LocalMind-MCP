# core/services/google_service.py
import logging
from typing import Any

import google.generativeai as genai

from .ai_service import AIResponse
from .ai_service import AIService

logger = logging.getLogger(__name__)


class GoogleService(AIService):
    """Google Gemini 服務實作"""

    def __init__(self, config: dict[str, Any]):
        super().__init__(config)

        if self.is_available():
            # 配置 Google AI
            genai.configure(api_key=self.api_key)

            # 初始化模型
            try:
                self.model_instance = genai.GenerativeModel(self.model)
            except Exception as e:
                logger.error(f"Google AI 模型初始化失敗：{e!s}")
                self.model_instance = None
                self.enabled = False
        else:
            self.model_instance = None
            logger.warning("Google 服務初始化失敗：缺少 API_KEY 或服務被禁用")

    def get_service_name(self) -> str:
        return "Google"

    def generate_response(
        self,
        messages: list[dict[str, str]],
        **kwargs,
    ) -> AIResponse:
        """
        使用 Google Gemini API 生成回覆

        Args:
            messages: 對話訊息列表
            **kwargs: 額外參數

        Returns:
            AIResponse: AI 回覆物件
        """
        try:
            # 檢查服務可用性
            if not self.is_available() or not self.model_instance:
                return self.format_error_response("Google 服務不可用：API_KEY 未設置或服務被禁用")

            # 驗證訊息格式
            if not self.validate_messages(messages):
                return self.format_error_response("無效的訊息格式")

            self.log_request(messages)

            # 將訊息轉換為 Google 格式
            formatted_content = self._format_messages_for_google(messages)

            # 設定生成配置
            generation_config = genai.types.GenerationConfig(
                max_output_tokens=kwargs.get("max_tokens", self.max_tokens),
                temperature=kwargs.get("temperature", self.temperature),
            )

            # 生成回應
            response = self.model_instance.generate_content(
                formatted_content,
                generation_config=generation_config,
            )

            # 解析回應
            if response.text:
                ai_response = AIResponse(
                    content=response.text.strip(),
                    model=self.model,
                    tokens_used=self._estimate_tokens(response.text),  # Google 不提供精確 token 計數
                    finish_reason=response.candidates[0].finish_reason.name if response.candidates else None,
                    metadata={
                        "candidates_count": len(response.candidates) if response.candidates else 0,
                        "safety_ratings": [
                            {
                                "category": rating.category.name,
                                "probability": rating.probability.name,
                            }
                            for rating in response.candidates[0].safety_ratings
                        ] if response.candidates and response.candidates[0].safety_ratings else [],
                    },
                )

                self.log_response(ai_response)
                return ai_response
            else:
                return self.format_error_response("Google API 回應為空")

        except Exception as e:
            error_msg = f"Google 服務錯誤：{e!s}"
            logger.error(error_msg, exc_info=True)
            return self.format_error_response(error_msg)

    def _format_messages_for_google(self, messages: list[dict[str, str]]) -> str:
        """
        將通用訊息格式轉換為 Google 格式

        Args:
            messages: 通用訊息格式

        Returns:
            str: Google 訊息格式
        """
        formatted_parts = []

        for message in messages:
            role = message["role"]
            content = message["content"]

            # 將角色轉換為中文描述
            if role == "system":
                prefix = "系統指示"
            elif role == "user":
                prefix = "使用者"
            elif role == "assistant":
                prefix = "助手"
            else:
                prefix = "訊息"

            formatted_parts.append(f"{prefix}：{content}")

        return "\n\n".join(formatted_parts)

    def _estimate_tokens(self, text: str) -> int:
        """
        估算 token 數量 (Google 不提供精確計數)

        Args:
            text: 文字內容

        Returns:
            int: 估算的 token 數量
        """
        # 粗略估算：英文 1 token ≈ 4 字元，中文 1 token ≈ 1.5 字元
        chinese_chars = sum(1 for char in text if "\u4e00" <= char <= "\u9fff")
        other_chars = len(text) - chinese_chars

        estimated_tokens = int(chinese_chars / 1.5 + other_chars / 4)
        return max(estimated_tokens, 1)

    def get_available_models(self) -> list[str]:
        """取得可用的模型列表"""
        try:
            if not self.is_available():
                return []

            models = genai.list_models()
            return [model.name for model in models if "generateContent" in model.supported_generation_methods]
        except Exception as e:
            logger.error(f"無法取得 Google 模型列表：{e!s}")
            return []
