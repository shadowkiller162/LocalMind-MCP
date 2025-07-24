"""
模型管理器

管理本地 LLM 模型的載入、卸載和使用。
"""

import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from ..config import get_config
from ..exceptions import MCPLLMError
from .client import OllamaClient
from .types import ModelInfo, LLMResponse, ChatMessage, GenerateRequest, ChatRequest


logger = logging.getLogger(__name__)


class ModelManager:
    """模型管理器"""
    
    def __init__(self, client: Optional[OllamaClient] = None):
        self.config = get_config()
        self.client = client or OllamaClient()
        self._available_models: Dict[str, ModelInfo] = {}
        self._model_cache: Dict[str, datetime] = {}
        self._lock = asyncio.Lock()
        self._initialized = False
    
    async def initialize(self) -> None:
        """初始化模型管理器"""
        async with self._lock:
            if self._initialized:
                return
            
            try:
                await self._refresh_available_models()
                self._initialized = True
                logger.info("Model manager initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize model manager: {e}")
                raise MCPLLMError(
                    f"Failed to initialize model manager: {e}",
                    llm_type="ollama"
                ) from e
    
    async def _refresh_available_models(self) -> None:
        """刷新可用模型列表"""
        try:
            async with self.client:
                models = await self.client.list_models()
                self._available_models = {model.name: model for model in models}
                logger.info(f"Refreshed {len(models)} available models")
        except Exception as e:
            logger.error(f"Failed to refresh models: {e}")
            raise
    
    async def list_models(self, refresh: bool = False) -> List[ModelInfo]:
        """列出可用模型"""
        if not self._initialized:
            await self.initialize()
        
        if refresh or not self._available_models:
            await self._refresh_available_models()
        
        return list(self._available_models.values())
    
    async def get_model_info(self, model_name: str) -> Optional[ModelInfo]:
        """取得模型資訊"""
        if not self._initialized:
            await self.initialize()
        
        return self._available_models.get(model_name)
    
    async def ensure_model_available(self, model_name: str) -> bool:
        """確保模型可用，如果不存在則嘗試拉取"""
        if not self._initialized:
            await self.initialize()
        
        # 檢查模型是否已經存在
        if model_name in self._available_models:
            return True
        
        # 嘗試拉取模型
        try:
            logger.info(f"Pulling model: {model_name}")
            async with self.client:
                success = await self.client.pull_model(model_name)
                
                if success:
                    # 刷新模型列表
                    await self._refresh_available_models()
                    return model_name in self._available_models
                
                return False
        
        except Exception as e:
            logger.error(f"Failed to pull model {model_name}: {e}")
            return False
    
    async def generate_text(
        self, 
        model_name: str, 
        prompt: str,
        context: Optional[List[int]] = None,
        options: Optional[Dict[str, any]] = None
    ) -> LLMResponse:
        """生成文本"""
        # 確保模型可用
        if not await self.ensure_model_available(model_name):
            raise MCPLLMError(
                f"Model {model_name} is not available",
                llm_type="ollama",
                model_name=model_name
            )
        
        # 更新模型使用時間
        self._model_cache[model_name] = datetime.now()
        
        # 建立生成請求
        request = GenerateRequest(
            model=model_name,
            prompt=prompt,
            context=context,
            options=options
        )
        
        try:
            async with self.client:
                response = await self.client.generate(request)
                logger.debug(f"Generated text for model {model_name}")
                return response
        
        except Exception as e:
            logger.error(f"Failed to generate text with model {model_name}: {e}")
            raise
    
    async def chat(
        self,
        model_name: str,
        messages: List[ChatMessage],
        options: Optional[Dict[str, any]] = None
    ) -> LLMResponse:
        """聊天對話"""
        # 確保模型可用
        if not await self.ensure_model_available(model_name):
            raise MCPLLMError(
                f"Model {model_name} is not available",
                llm_type="ollama", 
                model_name=model_name
            )
        
        # 更新模型使用時間
        self._model_cache[model_name] = datetime.now()
        
        # 建立聊天請求
        request = ChatRequest(
            model=model_name,
            messages=messages,
            options=options
        )
        
        try:
            async with self.client:
                response = await self.client.chat(request)
                logger.debug(f"Chat completed for model {model_name}")
                return response
        
        except Exception as e:
            logger.error(f"Failed to chat with model {model_name}: {e}")
            raise
    
    async def get_default_model(self) -> str:
        """取得預設模型"""
        if not self._initialized:
            await self.initialize()
        
        default_model = self.config.default_model
        
        # 檢查預設模型是否可用
        if default_model in self._available_models:
            return default_model
        
        # 如果預設模型不可用，嘗試使用第一個可用模型
        if self._available_models:
            available_model = next(iter(self._available_models.keys()))
            logger.warning(
                f"Default model {default_model} not available, "
                f"using {available_model} instead"
            )
            return available_model
        
        # 如果沒有可用模型，嘗試拉取預設模型
        if await self.ensure_model_available(default_model):
            return default_model
        
        raise MCPLLMError(
            "No models available and failed to pull default model",
            llm_type="ollama",
            model_name=default_model
        )
    
    async def health_check(self) -> bool:
        """健康檢查"""
        try:
            async with self.client:
                return await self.client.health_check()
        except Exception as e:
            logger.error(f"Model manager health check failed: {e}")
            return False
    
    def get_model_usage_stats(self) -> Dict[str, datetime]:
        """取得模型使用統計"""
        return self._model_cache.copy()
    
    def cleanup_unused_models(self, hours: int = 24) -> List[str]:
        """清理未使用的模型（僅標記，實際清理需要額外實作）"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        unused_models = [
            model_name for model_name, last_used in self._model_cache.items()
            if last_used < cutoff_time
        ]
        
        logger.info(f"Found {len(unused_models)} unused models")
        return unused_models
    
    async def cleanup(self) -> None:
        """清理管理器資源"""
        async with self._lock:
            self._available_models.clear()
            self._model_cache.clear()
            self._initialized = False
            logger.info("Model manager cleaned up")