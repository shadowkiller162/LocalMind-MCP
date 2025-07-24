"""
LM Studio 客戶端

與 LM Studio 本地 LLM 服務的整合客戶端。
LM Studio 提供與 OpenAI 相容的 API 介面。
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
import aiohttp

from ..config import get_config
from ..exceptions import MCPLLMError
from .types import (
    ModelInfo, LLMResponse, ChatMessage, GenerateRequest, 
    ChatRequest, LLMStatus
)


logger = logging.getLogger(__name__)


class LMStudioClient:
    """LM Studio 客戶端"""
    
    def __init__(self, host: Optional[str] = None, port: Optional[int] = None):
        self.config = get_config()
        self.host = host or self.config.lmstudio_host
        self.port = port or self.config.lmstudio_port
        self.base_url = f"http://{self.host}:{self.port}"
        self.timeout = self.config.lmstudio_timeout
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """異步上下文管理器入口"""
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """異步上下文管理器出口"""
        await self._close_session()
    
    async def _ensure_session(self):
        """確保 HTTP 會話存在"""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self._session = aiohttp.ClientSession(timeout=timeout)
    
    async def _close_session(self):
        """關閉 HTTP 會話"""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def _request(
        self, 
        method: str, 
        endpoint: str, 
        **kwargs
    ) -> Dict[str, Any]:
        """發送 HTTP 請求"""
        await self._ensure_session()
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            async with self._session.request(method, url, **kwargs) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise MCPLLMError(
                        f"LM Studio API error ({response.status}): {error_text}",
                        llm_type="lmstudio"
                    )
                
                return await response.json()
        
        except aiohttp.ClientError as e:
            raise MCPLLMError(
                f"Failed to connect to LM Studio: {e}",
                llm_type="lmstudio"
            ) from e
    
    async def list_models(self) -> List[ModelInfo]:
        """列出可用模型"""
        try:
            response = await self._request("GET", "/v1/models")
            models = []
            
            for model_data in response.get("data", []):
                model_info = ModelInfo(
                    name=model_data["id"],
                    size=None,  # LM Studio 不提供大小資訊
                    digest=None,
                    modified_at=str(model_data.get("created", "")),
                    details={
                        "object": model_data.get("object"),
                        "owned_by": model_data.get("owned_by", "lmstudio")
                    },
                    status=LLMStatus.AVAILABLE
                )
                models.append(model_info)
            
            logger.info(f"Found {len(models)} available models in LM Studio")
            return models
        
        except Exception as e:
            logger.error(f"Failed to list LM Studio models: {e}")
            raise MCPLLMError(
                f"Failed to list models: {e}",
                llm_type="lmstudio"
            ) from e
    
    async def generate(self, request: GenerateRequest) -> LLMResponse:
        """生成文本 (轉換為聊天格式)"""
        # LM Studio 主要使用聊天 API，將 generate 轉換為 chat
        chat_request = ChatRequest(
            model=request.model,
            messages=[
                ChatMessage(role="user", content=request.prompt)
            ],
            stream=False,
            options=request.options
        )
        
        return await self.chat(chat_request)
    
    async def chat(self, request: ChatRequest) -> LLMResponse:
        """聊天對話"""
        try:
            data = {
                "model": request.model,
                "messages": [
                    {"role": msg.role, "content": msg.content}
                    for msg in request.messages
                ],
                "stream": False,
                "temperature": 0.7,
                "max_tokens": -1,
            }
            
            # 添加額外選項
            if request.options:
                for key, value in request.options.items():
                    if key in ["temperature", "max_tokens", "top_p", "frequency_penalty"]:
                        data[key] = value
            
            response = await self._request("POST", "/v1/chat/completions", json=data)
            
            # 解析 OpenAI 格式的回應
            choice = response["choices"][0]
            message = choice["message"]
            
            return LLMResponse(
                content=message["content"],
                model=response["model"],
                created_at=str(response.get("created", "")),
                done=choice.get("finish_reason") == "stop",
                total_duration=None,  # LM Studio 不提供詳細時間
                load_duration=None,
                prompt_eval_count=response.get("usage", {}).get("prompt_tokens"),
                prompt_eval_duration=None,
                eval_count=response.get("usage", {}).get("completion_tokens"),
                eval_duration=None,
                context=None
            )
        
        except Exception as e:
            logger.error(f"Failed to chat with LM Studio: {e}")
            raise MCPLLMError(
                f"Failed to chat: {e}",
                llm_type="lmstudio",
                model_name=request.model
            ) from e
    
    async def health_check(self) -> bool:
        """健康檢查"""
        try:
            # 嘗試列出模型來檢查服務是否正常
            await self.list_models()
            return True
        except Exception as e:
            logger.warning(f"LM Studio health check failed: {e}")
            return False
    
    async def get_current_model(self) -> Optional[str]:
        """獲取當前載入的模型"""
        try:
            models = await self.list_models()
            if models:
                # 假設第一個模型是當前載入的模型
                return models[0].name
            return None
        except Exception:
            return None
    
    def __del__(self):
        """析構函數，確保會話被關閉"""
        if self._session and not self._session.closed:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self._close_session())
                else:
                    loop.run_until_complete(self._close_session())
            except RuntimeError:
                pass