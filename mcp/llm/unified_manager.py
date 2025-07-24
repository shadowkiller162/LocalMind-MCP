"""
統一模型管理器

支援多種本地 LLM 服務的統一管理器，包括 Ollama 和 LM Studio。
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, Any
from datetime import datetime, timedelta
from enum import Enum

from ..config import get_config
from ..exceptions import MCPLLMError
from .client import OllamaClient
from .lmstudio_client import LMStudioClient
from .types import ModelInfo, LLMResponse, ChatMessage, GenerateRequest, ChatRequest


logger = logging.getLogger(__name__)


class LLMServiceType(Enum):
    """LLM 服务类型"""
    OLLAMA = "ollama"
    LMSTUDIO = "lmstudio"
    AUTO = "auto"


class UnifiedModelManager:
    """統一模型管理器"""
    
    def __init__(self, preferred_service: LLMServiceType = LLMServiceType.AUTO):
        self.config = get_config()
        self.preferred_service = preferred_service
        self._ollama_client: Optional[OllamaClient] = None
        self._lmstudio_client: Optional[LMStudioClient] = None
        self._available_services: Dict[LLMServiceType, bool] = {}
        self._service_models: Dict[LLMServiceType, List[ModelInfo]] = {}
        self._model_cache: Dict[str, datetime] = {}
        self._lock = asyncio.Lock()
        self._initialized = False
    
    async def initialize(self) -> None:
        """初始化統一管理器"""
        async with self._lock:
            if self._initialized:
                return
            
            try:
                # 初始化客戶端
                self._ollama_client = OllamaClient()
                self._lmstudio_client = LMStudioClient()
                
                # 檢查服務可用性
                await self._check_service_availability()
                
                # 載入所有可用模型
                await self._refresh_all_models()
                
                self._initialized = True
                logger.info("Unified model manager initialized successfully")
                
                # 記錄可用服務
                available_services = [
                    service.value for service, available 
                    in self._available_services.items() if available
                ]
                logger.info(f"Available LLM services: {available_services}")
                
            except Exception as e:
                logger.error(f"Failed to initialize unified model manager: {e}")
                raise MCPLLMError(
                    f"Failed to initialize unified model manager: {e}",
                    llm_type="unified"
                ) from e
    
    async def _check_service_availability(self) -> None:
        """檢查所有服務的可用性"""
        # 檢查 Ollama
        try:
            ollama_healthy = await self._ollama_client.health_check()
            self._available_services[LLMServiceType.OLLAMA] = ollama_healthy
            if ollama_healthy:
                logger.info("Ollama service is available")
        except Exception as e:
            logger.warning(f"Ollama service not available: {e}")
            self._available_services[LLMServiceType.OLLAMA] = False
        
        # 檢查 LM Studio
        try:
            lmstudio_healthy = await self._lmstudio_client.health_check()
            self._available_services[LLMServiceType.LMSTUDIO] = lmstudio_healthy
            if lmstudio_healthy:
                logger.info("LM Studio service is available")
        except Exception as e:
            logger.warning(f"LM Studio service not available: {e}")
            self._available_services[LLMServiceType.LMSTUDIO] = False
    
    async def _refresh_all_models(self) -> None:
        """刷新所有服務的模型列表"""
        # 獲取 Ollama 模型
        if self._available_services.get(LLMServiceType.OLLAMA, False):
            try:
                async with self._ollama_client:
                    ollama_models = await self._ollama_client.list_models()
                    # 為模型名稱添加服務前綴
                    for model in ollama_models:
                        model.name = f"ollama:{model.name}"
                    self._service_models[LLMServiceType.OLLAMA] = ollama_models
                    logger.info(f"Loaded {len(ollama_models)} Ollama models")
            except Exception as e:
                logger.error(f"Failed to load Ollama models: {e}")
                self._service_models[LLMServiceType.OLLAMA] = []
        
        # 獲取 LM Studio 模型
        if self._available_services.get(LLMServiceType.LMSTUDIO, False):
            try:
                async with self._lmstudio_client:
                    lmstudio_models = await self._lmstudio_client.list_models()
                    # 為模型名稱添加服務前綴
                    for model in lmstudio_models:
                        model.name = f"lmstudio:{model.name}"
                    self._service_models[LLMServiceType.LMSTUDIO] = lmstudio_models
                    logger.info(f"Loaded {len(lmstudio_models)} LM Studio models")
            except Exception as e:
                logger.error(f"Failed to load LM Studio models: {e}")
                self._service_models[LLMServiceType.LMSTUDIO] = []
    
    def _parse_model_name(self, model_name: str) -> tuple[LLMServiceType, str]:
        """解析模型名稱，返回服務類型和實際模型名稱"""
        if model_name.startswith("ollama:"):
            return LLMServiceType.OLLAMA, model_name[7:]  # 移除 "ollama:" 前綴
        elif model_name.startswith("lmstudio:"):
            return LLMServiceType.LMSTUDIO, model_name[9:]  # 移除 "lmstudio:" 前綴
        else:
            # 沒有前綴，使用偏好服務或自動選擇
            if self.preferred_service != LLMServiceType.AUTO:
                return self.preferred_service, model_name
            else:
                # 自動選擇第一個可用服務
                for service, available in self._available_services.items():
                    if available and service != LLMServiceType.AUTO:
                        return service, model_name
                raise MCPLLMError("No available LLM service", llm_type="unified")
    
    async def list_models(self, refresh: bool = False) -> List[ModelInfo]:
        """列出所有可用模型"""
        if not self._initialized:
            await self.initialize()
        
        if refresh:
            await self._refresh_all_models()
        
        all_models = []
        for service_models in self._service_models.values():
            all_models.extend(service_models)
        
        return all_models
    
    async def get_model_info(self, model_name: str) -> Optional[ModelInfo]:
        """取得模型資訊"""
        if not self._initialized:
            await self.initialize()
        
        service_type, actual_name = self._parse_model_name(model_name)
        
        service_models = self._service_models.get(service_type, [])
        for model in service_models:
            if actual_name in model.name:
                return model
        
        return None
    
    async def generate_text(
        self, 
        model_name: str, 
        prompt: str,
        options: Optional[Dict[str, Any]] = None
    ) -> LLMResponse:
        """生成文本"""
        if not self._initialized:
            await self.initialize()
        
        service_type, actual_name = self._parse_model_name(model_name)
        
        if not self._available_services.get(service_type, False):
            raise MCPLLMError(
                f"Service {service_type.value} is not available",
                llm_type=service_type.value,
                model_name=model_name
            )
        
        # 更新模型使用時間
        self._model_cache[model_name] = datetime.now()
        
        # 建立生成請求
        request = GenerateRequest(
            model=actual_name,
            prompt=prompt,
            options=options
        )
        
        try:
            if service_type == LLMServiceType.OLLAMA:
                async with self._ollama_client:
                    response = await self._ollama_client.generate(request)
            elif service_type == LLMServiceType.LMSTUDIO:
                async with self._lmstudio_client:
                    response = await self._lmstudio_client.generate(request)
            else:
                raise MCPLLMError(f"Unsupported service type: {service_type}")
            
            logger.debug(f"Generated text using {service_type.value}:{actual_name}")
            return response
        
        except Exception as e:
            logger.error(f"Failed to generate text with {service_type.value}: {e}")
            raise
    
    async def chat(
        self,
        model_name: str,
        messages: List[ChatMessage],
        options: Optional[Dict[str, Any]] = None
    ) -> LLMResponse:
        """聊天對話"""
        if not self._initialized:
            await self.initialize()
        
        service_type, actual_name = self._parse_model_name(model_name)
        
        if not self._available_services.get(service_type, False):
            raise MCPLLMError(
                f"Service {service_type.value} is not available",
                llm_type=service_type.value,
                model_name=model_name
            )
        
        # 更新模型使用時間
        self._model_cache[model_name] = datetime.now()
        
        # 建立聊天請求
        request = ChatRequest(
            model=actual_name,
            messages=messages,
            options=options
        )
        
        try:
            if service_type == LLMServiceType.OLLAMA:
                async with self._ollama_client:
                    response = await self._ollama_client.chat(request)
            elif service_type == LLMServiceType.LMSTUDIO:
                async with self._lmstudio_client:
                    response = await self._lmstudio_client.chat(request)
            else:
                raise MCPLLMError(f"Unsupported service type: {service_type}")
            
            logger.debug(f"Chat completed using {service_type.value}:{actual_name}")
            return response
        
        except Exception as e:
            logger.error(f"Failed to chat with {service_type.value}: {e}")
            raise
    
    async def get_available_services(self) -> Dict[str, bool]:
        """取得可用服務狀態"""
        if not self._initialized:
            await self.initialize()
        
        return {
            service.value: available 
            for service, available in self._available_services.items()
            if service != LLMServiceType.AUTO
        }
    
    async def get_recommended_model(self) -> Optional[str]:
        """取得推薦的模型"""
        if not self._initialized:
            await self.initialize()
        
        all_models = await self.list_models()
        
        if not all_models:
            return None
        
        # 優先推薦 LM Studio 中的 DeepSeek 模型
        for model in all_models:
            if "lmstudio" in model.name and "deepseek" in model.name.lower():
                return model.name
        
        # 其次推薦任何 LM Studio 模型
        for model in all_models:
            if "lmstudio" in model.name:
                return model.name
        
        # 最後推薦第一個可用模型
        return all_models[0].name
    
    async def health_check(self) -> Dict[str, bool]:
        """健康檢查所有服務"""
        if not self._initialized:
            await self.initialize()
        
        health_status = {}
        
        # 檢查 Ollama
        if self._ollama_client:
            try:
                async with self._ollama_client:
                    health_status["ollama"] = await self._ollama_client.health_check()
            except Exception:
                health_status["ollama"] = False
        
        # 檢查 LM Studio
        if self._lmstudio_client:
            try:
                async with self._lmstudio_client:
                    health_status["lmstudio"] = await self._lmstudio_client.health_check()
            except Exception:
                health_status["lmstudio"] = False
        
        return health_status
    
    async def cleanup(self) -> None:
        """清理管理器資源"""
        async with self._lock:
            self._service_models.clear()
            self._model_cache.clear()
            self._available_services.clear()
            self._initialized = False
            logger.info("Unified model manager cleaned up")