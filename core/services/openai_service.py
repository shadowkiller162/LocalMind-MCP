# core/services/openai_service.py
import logging
from typing import Any

import openai

from .ai_service import AIResponse
from .ai_service import AIService

logger = logging.getLogger(__name__)


class OpenAIService(AIService):
    """OpenAI GPT 服務實作"""

    def __init__(self, config: dict[str, Any]):
        super().__init__(config)

        if self.is_available():
            # 初始化 OpenAI 客戶端
            self.client = openai.OpenAI(
                api_key=self.api_key,
                timeout=self.timeout,
            )
        else:
            self.client = None
            logger.warning("OpenAI 服務初始化失敗：缺少 API_KEY 或服務被禁用")

    def get_service_name(self) -> str:
        return "OpenAI"

    def generate_response(
        self,
        messages: list[dict[str, str]],
        **kwargs,
    ) -> AIResponse:
        """
        使用 OpenAI API 生成回覆

        Args:
            messages: 對話訊息列表
            **kwargs: 額外參數

        Returns:
            AIResponse: AI 回覆物件
        """
        try:
            # 檢查服務可用性
            if not self.is_available():
                return self.format_error_response("OpenAI 服務不可用：API_KEY 未設置或服務被禁用")

            # 驗證訊息格式
            if not self.validate_messages(messages):
                return self.format_error_response("無效的訊息格式")

            self.log_request(messages)

            # 處理額外參數
            request_params = {
                "model": kwargs.get("model", self.model),
                "messages": messages,
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                "temperature": kwargs.get("temperature", self.temperature),
                "stream": False,
            }

            # 呼叫 OpenAI API
            response = self.client.chat.completions.create(**request_params)

            # 解析回應
            if response.choices and len(response.choices) > 0:
                choice = response.choices[0]
                content = choice.message.content or ""

                ai_response = AIResponse(
                    content=content.strip(),
                    model=response.model,
                    tokens_used=response.usage.total_tokens if response.usage else None,
                    finish_reason=choice.finish_reason,
                    metadata={
                        "prompt_tokens": response.usage.prompt_tokens if response.usage else None,
                        "completion_tokens": response.usage.completion_tokens if response.usage else None,
                    },
                )

                self.log_response(ai_response)
                return ai_response
            else:
                return self.format_error_response("OpenAI API 回應為空")

        except openai.AuthenticationError as e:
            error_msg = f"OpenAI 認證失敗：{e!s}"
            logger.error(error_msg)
            return self.format_error_response(error_msg)

        except openai.RateLimitError as e:
            error_msg = f"OpenAI API 限流：{e!s}"
            logger.error(error_msg)
            return self.format_error_response(error_msg)

        except openai.APITimeoutError as e:
            error_msg = f"OpenAI API 超時：{e!s}"
            logger.error(error_msg)
            return self.format_error_response(error_msg)

        except openai.APIError as e:
            error_msg = f"OpenAI API 錯誤：{e!s}"
            logger.error(error_msg)
            return self.format_error_response(error_msg)

        except Exception as e:
            error_msg = f"OpenAI 服務未知錯誤：{e!s}"
            logger.error(error_msg, exc_info=True)
            return self.format_error_response(error_msg)

    def get_available_models(self) -> list[str]:
        """取得可用的模型列表"""
        try:
            if not self.is_available():
                return []

            models = self.client.models.list()
            return [model.id for model in models.data if "gpt" in model.id]
        except Exception as e:
            logger.error(f"無法取得 OpenAI 模型列表：{e!s}")
            return []
