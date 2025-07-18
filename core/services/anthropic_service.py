# core/services/anthropic_service.py
import logging
from typing import Any

import anthropic

from .ai_service import AIResponse
from .ai_service import AIService

logger = logging.getLogger(__name__)


class AnthropicService(AIService):
    """Anthropic Claude 服務實作"""

    def __init__(self, config: dict[str, Any]):
        super().__init__(config)

        if self.is_available():
            # 初始化 Anthropic 客戶端
            self.client = anthropic.Anthropic(
                api_key=self.api_key,
                timeout=self.timeout,
            )
        else:
            self.client = None
            logger.warning("Anthropic 服務初始化失敗：缺少 API_KEY 或服務被禁用")

    def get_service_name(self) -> str:
        return "Anthropic"

    def generate_response(
        self,
        messages: list[dict[str, str]],
        **kwargs,
    ) -> AIResponse:
        """
        使用 Anthropic API 生成回覆

        Args:
            messages: 對話訊息列表
            **kwargs: 額外參數

        Returns:
            AIResponse: AI 回覆物件
        """
        try:
            # 檢查服務可用性
            if not self.is_available():
                return self.format_error_response("Anthropic 服務不可用：API_KEY 未設置或服務被禁用")

            # 驗證訊息格式
            if not self.validate_messages(messages):
                return self.format_error_response("無效的訊息格式")

            self.log_request(messages)

            # 轉換訊息格式給 Anthropic
            formatted_messages = self._format_messages_for_anthropic(messages)

            # 處理額外參數
            request_params = {
                "model": kwargs.get("model", self.model),
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                "temperature": kwargs.get("temperature", self.temperature),
                "messages": formatted_messages,
            }

            # 呼叫 Anthropic API
            response = self.client.messages.create(**request_params)

            # 解析回應
            if response.content and len(response.content) > 0:
                # Anthropic 回應是 ContentBlock 列表
                content = ""
                for block in response.content:
                    if hasattr(block, "text"):
                        content += block.text
                    elif isinstance(block, str):
                        content += block

                ai_response = AIResponse(
                    content=content.strip(),
                    model=response.model,
                    tokens_used=response.usage.output_tokens + response.usage.input_tokens if response.usage else None,
                    finish_reason=response.stop_reason,
                    metadata={
                        "input_tokens": response.usage.input_tokens if response.usage else None,
                        "output_tokens": response.usage.output_tokens if response.usage else None,
                    },
                )

                self.log_response(ai_response)
                return ai_response
            else:
                return self.format_error_response("Anthropic API 回應為空")

        except anthropic.AuthenticationError as e:
            error_msg = f"Anthropic 認證失敗：{e!s}"
            logger.error(error_msg)
            return self.format_error_response(error_msg)

        except anthropic.RateLimitError as e:
            error_msg = f"Anthropic API 限流：{e!s}"
            logger.error(error_msg)
            return self.format_error_response(error_msg)

        except anthropic.APITimeoutError as e:
            error_msg = f"Anthropic API 超時：{e!s}"
            logger.error(error_msg)
            return self.format_error_response(error_msg)

        except anthropic.APIError as e:
            error_msg = f"Anthropic API 錯誤：{e!s}"
            logger.error(error_msg)
            return self.format_error_response(error_msg)

        except Exception as e:
            error_msg = f"Anthropic 服務未知錯誤：{e!s}"
            logger.error(error_msg, exc_info=True)
            return self.format_error_response(error_msg)

    def _format_messages_for_anthropic(self, messages: list[dict[str, str]]) -> list[dict[str, str]]:
        """
        將通用訊息格式轉換為 Anthropic 格式

        Args:
            messages: 通用訊息格式

        Returns:
            List[Dict]: Anthropic 訊息格式
        """
        formatted = []

        for message in messages:
            role = message["role"]
            content = message["content"]

            # Anthropic 不支援 system role，將其轉換為 assistant
            if role == "system":
                role = "assistant"

            formatted.append({
                "role": role,
                "content": content,
            })

        return formatted
