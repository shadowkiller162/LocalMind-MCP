"""
Ollama 客戶端

與 Ollama LLM 服務的整合客戶端。
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, AsyncGenerator
import aiohttp

from ..config import get_config
from ..exceptions import MCPLLMError
from .types import (
    ModelInfo, LLMResponse, ChatMessage, GenerateRequest, 
    ChatRequest, LLMStatus
)


logger = logging.getLogger(__name__)


class OllamaClient:
    """Ollama 客戶端"""
    
    def __init__(self, host: Optional[str] = None, port: Optional[int] = None):
        self.config = get_config()
        self.host = host or self.config.ollama_host
        self.port = port or self.config.ollama_port
        self.base_url = f"http://{self.host}:{self.port}"
        self.timeout = self.config.ollama_timeout
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
    ) -> Dict[str, any]:
        """發送 HTTP 請求"""
        await self._ensure_session()
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            async with self._session.request(method, url, **kwargs) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise MCPLLMError(
                        f"Ollama API error ({response.status}): {error_text}",
                        llm_type="ollama"
                    )
                
                return await response.json()
        
        except aiohttp.ClientError as e:
            raise MCPLLMError(
                f"Failed to connect to Ollama: {e}",
                llm_type="ollama"
            ) from e
    
    async def list_models(self) -> List[ModelInfo]:
        """列出可用模型"""
        try:
            response = await self._request("GET", "/api/tags")
            models = []
            
            for model_data in response.get("models", []):
                model_info = ModelInfo(
                    name=model_data["name"],
                    size=model_data.get("size"),
                    digest=model_data.get("digest"),
                    modified_at=model_data.get("modified_at"),
                    details=model_data.get("details"),
                    status=LLMStatus.AVAILABLE
                )
                models.append(model_info)
            
            logger.info(f"Found {len(models)} available models")
            return models
        
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            raise MCPLLMError(
                f"Failed to list models: {e}",
                llm_type="ollama"
            ) from e
    
    async def pull_model(self, model_name: str) -> bool:
        """拉取模型"""
        try:
            data = {"name": model_name}
            
            # 這是一個流式響應，我們需要等待完成
            await self._ensure_session()
            url = f"{self.base_url}/api/pull"
            
            async with self._session.post(url, json=data) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise MCPLLMError(
                        f"Failed to pull model {model_name}: {error_text}",
                        llm_type="ollama",
                        model_name=model_name
                    )
                
                # 讀取流式響應直到完成
                async for line in response.content:
                    if line:
                        try:
                            chunk_data = json.loads(line.decode())
                            if chunk_data.get("status") == "success":
                                logger.info(f"Successfully pulled model: {model_name}")
                                return True
                        except json.JSONDecodeError:
                            continue
            
            return True
        
        except Exception as e:
            logger.error(f"Failed to pull model {model_name}: {e}")
            raise MCPLLMError(
                f"Failed to pull model {model_name}: {e}",
                llm_type="ollama",
                model_name=model_name
            ) from e
    
    async def generate(self, request: GenerateRequest) -> LLMResponse:
        """生成文本"""
        try:
            data = {
                "model": request.model,
                "prompt": request.prompt,
                "stream": False,  # 目前只支援非流式
            }
            
            if request.context:
                data["context"] = request.context
            if request.options:
                data["options"] = request.options
            
            response = await self._request("POST", "/api/generate", json=data)
            
            return LLMResponse(
                content=response["response"],
                model=response["model"],
                created_at=response["created_at"],
                done=response.get("done", True),
                total_duration=response.get("total_duration"),
                load_duration=response.get("load_duration"),
                prompt_eval_count=response.get("prompt_eval_count"),
                prompt_eval_duration=response.get("prompt_eval_duration"),
                eval_count=response.get("eval_count"),
                eval_duration=response.get("eval_duration"),
                context=response.get("context"),
            )
        
        except Exception as e:
            logger.error(f"Failed to generate text: {e}")
            raise MCPLLMError(
                f"Failed to generate text: {e}",
                llm_type="ollama",
                model_name=request.model
            ) from e
    
    async def chat(self, request: ChatRequest) -> LLMResponse:
        """聊天對話"""
        try:
            data = {
                "model": request.model,
                "messages": [
                    {"role": msg.role, "content": msg.content}
                    for msg in request.messages
                ],
                "stream": False,  # 目前只支援非流式
            }
            
            if request.options:
                data["options"] = request.options
            
            response = await self._request("POST", "/api/chat", json=data)
            
            # 從回應中取得助理的回覆
            assistant_message = response["message"]
            
            return LLMResponse(
                content=assistant_message["content"],
                model=response["model"],
                created_at=response["created_at"],
                done=response.get("done", True),
                total_duration=response.get("total_duration"),
                load_duration=response.get("load_duration"),
                prompt_eval_count=response.get("prompt_eval_count"),
                prompt_eval_duration=response.get("prompt_eval_duration"),
                eval_count=response.get("eval_count"),
                eval_duration=response.get("eval_duration"),
            )
        
        except Exception as e:
            logger.error(f"Failed to chat: {e}")
            raise MCPLLMError(
                f"Failed to chat: {e}",
                llm_type="ollama",
                model_name=request.model
            ) from e
    
    async def health_check(self) -> bool:
        """健康檢查"""
        try:
            # 嘗試列出模型來檢查服務是否正常
            await self.list_models()
            return True
        except Exception as e:
            logger.warning(f"Ollama health check failed: {e}")
            return False
    
    def __del__(self):
        """析構函數，確保會話被關閉"""
        if self._session and not self._session.closed:
            # 在事件循環中安排關閉會話
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self._close_session())
                else:
                    loop.run_until_complete(self._close_session())
            except RuntimeError:
                # 如果沒有事件循環，就忽略
                pass