---
name: Code Optimization - unified_manager.py
about: Optimize unified_manager.py following Linus methodology (332 lines → <300 lines)
title: 'refactor: Extract service discovery and caching from unified_manager.py'
labels: 'refactoring, technical-debt, medium-priority, prevention'
assignees: ''
---

## 📋 問題描述

**當前狀態：**
- 文件：`mcp/llm/unified_manager.py`
- 行數：332 / 300（超標 10%）🟡
- 類別：`UnifiedModelManager`（管理器類）
- 職責：服務發現 + 模型管理 + 緩存管理 + 健康檢查

**警告狀態：**
根據 [CLAUDE.md](../../CLAUDE.md) Linus 方法論：
- ⚠️ 文件行數：332 / 300（臨界點）
- ⚠️ 再加任何新功能都會超標
- ⚠️ 職責開始混亂（管理器做了太多事）

**核心問題：**
```
【品味評分】
🟡 湊合 - 332 行勉強可以接受，但再加功能就炸了

【警告】
- 這是個管理器類，職責相對單一
- 但已經在臨界點，任何新功能都會讓它爆炸
- 現在還來得及預防性重構
```

## 🎯 重構目標

**可測量指標：**
- ✅ 主文件 < 200 行
- ✅ 每個類別職責單一
- ✅ 服務發現邏輯獨立
- ✅ 模型緩存邏輯獨立

**預期結構：**
```
mcp/llm/
├── unified_manager.py (180 行) - 簡化的管理器
├── service_discovery.py (100 行) - 服務發現邏輯
├── model_cache.py (120 行) - 模型緩存管理
└── health_checker.py (80 行) - 健康檢查邏輯
```

**設計原則：**
- UnifiedModelManager 只做**協調**，不做具體工作
- 依賴注入：可以替換 ServiceDiscovery/ModelCache 實作
- 單一職責：每個類別只做一件事

## 🔧 實作步驟

### Phase 1: 提取服務發現邏輯

**步驟 1.1: 創建 ServiceDiscovery 類別**
創建 `mcp/llm/service_discovery.py`：
```python
"""LLM 服務發現模組"""
import asyncio
import logging
from typing import Dict, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class LLMServiceType(Enum):
    """LLM 服務類型"""
    OLLAMA = "ollama"
    LMSTUDIO = "lmstudio"
    AUTO = "auto"


class ServiceDiscovery:
    """LLM 服務發現器"""

    def __init__(self, ollama_client, lmstudio_client):
        self.ollama_client = ollama_client
        self.lmstudio_client = lmstudio_client
        self._available_services: Dict[LLMServiceType, bool] = {}

    async def discover_services(self) -> Dict[LLMServiceType, bool]:
        """發現所有可用的 LLM 服務

        Returns:
            Dict[LLMServiceType, bool]: 服務可用性映射
        """
        await asyncio.gather(
            self._check_ollama(),
            self._check_lmstudio(),
            return_exceptions=True
        )
        return self._available_services

    async def _check_ollama(self) -> None:
        """檢查 Ollama 服務可用性"""
        try:
            healthy = await self.ollama_client.health_check()
            self._available_services[LLMServiceType.OLLAMA] = healthy
            if healthy:
                logger.info("Ollama service is available")
        except Exception as e:
            logger.warning(f"Ollama service not available: {e}")
            self._available_services[LLMServiceType.OLLAMA] = False

    async def _check_lmstudio(self) -> None:
        """檢查 LM Studio 服務可用性"""
        try:
            healthy = await self.lmstudio_client.health_check()
            self._available_services[LLMServiceType.LMSTUDIO] = healthy
            if healthy:
                logger.info("LM Studio service is available")
        except Exception as e:
            logger.warning(f"LM Studio service not available: {e}")
            self._available_services[LLMServiceType.LMSTUDIO] = False

    def is_service_available(self, service_type: LLMServiceType) -> bool:
        """檢查特定服務是否可用"""
        return self._available_services.get(service_type, False)

    def get_available_services(self) -> list[LLMServiceType]:
        """取得所有可用服務列表"""
        return [
            service for service, available
            in self._available_services.items()
            if available
        ]
```

### Phase 2: 提取模型緩存邏輯

**步驟 2.1: 創建 ModelCache 類別**
創建 `mcp/llm/model_cache.py`：
```python
"""模型緩存管理模組"""
import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from .types import ModelInfo
from .service_discovery import LLMServiceType

logger = logging.getLogger(__name__)


class ModelCache:
    """模型信息緩存管理器"""

    def __init__(self, cache_ttl: int = 300):
        """
        Args:
            cache_ttl: 緩存有效期（秒），預設 5 分鐘
        """
        self.cache_ttl = cache_ttl
        self._service_models: Dict[LLMServiceType, List[ModelInfo]] = {}
        self._model_cache: Dict[str, datetime] = {}
        self._lock = asyncio.Lock()

    async def get_models(
        self,
        service_type: LLMServiceType,
        force_refresh: bool = False
    ) -> List[ModelInfo]:
        """取得服務的模型列表

        Args:
            service_type: LLM 服務類型
            force_refresh: 是否強制刷新緩存

        Returns:
            List[ModelInfo]: 模型列表
        """
        async with self._lock:
            if force_refresh or self._is_cache_expired(service_type):
                return []  # 需要刷新
            return self._service_models.get(service_type, [])

    async def set_models(
        self,
        service_type: LLMServiceType,
        models: List[ModelInfo]
    ) -> None:
        """設置服務的模型列表

        Args:
            service_type: LLM 服務類型
            models: 模型列表
        """
        async with self._lock:
            self._service_models[service_type] = models
            self._model_cache[service_type.value] = datetime.now()
            logger.debug(f"Cached {len(models)} models for {service_type.value}")

    def _is_cache_expired(self, service_type: LLMServiceType) -> bool:
        """檢查緩存是否過期"""
        cache_time = self._model_cache.get(service_type.value)
        if not cache_time:
            return True

        age = datetime.now() - cache_time
        return age > timedelta(seconds=self.cache_ttl)

    async def clear_cache(self, service_type: Optional[LLMServiceType] = None) -> None:
        """清除緩存

        Args:
            service_type: 指定服務類型，None 則清除全部
        """
        async with self._lock:
            if service_type:
                self._service_models.pop(service_type, None)
                self._model_cache.pop(service_type.value, None)
            else:
                self._service_models.clear()
                self._model_cache.clear()
```

### Phase 3: 簡化 UnifiedModelManager

**步驟 3.1: 重構主管理器**
修改 `mcp/llm/unified_manager.py`：
```python
"""統一模型管理器"""
import asyncio
import logging
from typing import Optional

from ..config import get_config
from ..exceptions import MCPLLMError
from .client import OllamaClient
from .lmstudio_client import LMStudioClient
from .service_discovery import ServiceDiscovery, LLMServiceType
from .model_cache import ModelCache

logger = logging.getLogger(__name__)


class UnifiedModelManager:
    """統一模型管理器（簡化版）"""

    def __init__(
        self,
        preferred_service: LLMServiceType = LLMServiceType.AUTO,
        cache_ttl: int = 300
    ):
        self.config = get_config()
        self.preferred_service = preferred_service

        # 客戶端
        self._ollama_client: Optional[OllamaClient] = None
        self._lmstudio_client: Optional[LMStudioClient] = None

        # 依賴注入的組件
        self.service_discovery: Optional[ServiceDiscovery] = None
        self.model_cache: Optional[ModelCache] = None

        self._initialized = False
        self._lock = asyncio.Lock()

    async def initialize(self) -> None:
        """初始化統一管理器"""
        async with self._lock:
            if self._initialized:
                return

            try:
                # 初始化客戶端
                self._ollama_client = OllamaClient()
                self._lmstudio_client = LMStudioClient()

                # 初始化組件
                self.service_discovery = ServiceDiscovery(
                    self._ollama_client,
                    self._lmstudio_client
                )
                self.model_cache = ModelCache(cache_ttl=300)

                # 發現服務
                await self.service_discovery.discover_services()

                # 載入模型
                await self._load_all_models()

                self._initialized = True
                logger.info("Unified model manager initialized successfully")

            except Exception as e:
                logger.error(f"Failed to initialize: {e}")
                raise MCPLLMError(f"Initialization failed: {e}") from e

    async def _load_all_models(self) -> None:
        """載入所有可用服務的模型"""
        available_services = self.service_discovery.get_available_services()

        for service_type in available_services:
            try:
                models = await self._fetch_models_for_service(service_type)
                await self.model_cache.set_models(service_type, models)
            except Exception as e:
                logger.warning(f"Failed to load models for {service_type}: {e}")

    async def _fetch_models_for_service(self, service_type: LLMServiceType):
        """獲取特定服務的模型列表"""
        if service_type == LLMServiceType.OLLAMA:
            return await self._ollama_client.list_models()
        elif service_type == LLMServiceType.LMSTUDIO:
            return await self._lmstudio_client.list_models()
        return []

    # ... 其他方法保持簡潔
```

## ✅ 驗收標準

### 代碼品質
- [ ] unified_manager.py < 200 行
- [ ] 新增文件各 < 150 行
- [ ] 所有類別職責單一
- [ ] mypy 檢查通過（0 錯誤）
- [ ] ruff 檢查通過（0 警告）

### 功能測試
- [ ] 所有現有測試通過
- [ ] 服務發現正常運作
- [ ] 模型列表獲取正確
- [ ] 緩存機制正常
- [ ] 健康檢查功能正常

### 架構檢查
- [ ] UnifiedModelManager 只做協調
- [ ] ServiceDiscovery 可獨立測試
- [ ] ModelCache 可獨立測試
- [ ] 依賴注入設計正確

### 向後相容性
- [ ] 現有 API 簽名不變
- [ ] 功能零破壞
- [ ] 導入路徑保持一致

## 🔄 回滾計劃

**Git 標籤：** `before-manager-optimize`

**回滾命令：**
```bash
git tag before-manager-optimize  # 優化前打標籤
git reset --hard before-manager-optimize  # 如需回滾
```

**驗證腳本：**
```bash
# 檢查文件大小
wc -l mcp/llm/unified_manager.py
find mcp/llm -name "*.py" -exec wc -l {} +

# 運行測試
docker compose exec django pytest mcp/tests/ -k "unified" -v

# 檢查代碼品質
docker compose exec django ruff check mcp/llm/
docker compose exec django mypy mcp/llm/
```

## 📊 預期收益

**可測量改進：**
- 主文件：332 行 → ~180 行 ✅
- 文件數量：1 個 → 4 個（職責清晰）✅
- 最大類別：UnifiedModelManager → 簡化的協調器 ✅
- 技術債等級：🟡 MEDIUM → 🟢 LOW

**長期價值：**
- ✅ 預防性重構（趁還簡單時處理）
- ✅ 更容易測試（組件可獨立測試）
- ✅ 更容易擴展（新增服務類型更簡單）
- ✅ 更容易維護（職責清晰）

## 💡 未來擴展示例

新增支援 `OpenAI` 服務（示例）：
```python
# 1. 在 ServiceDiscovery 中添加
async def _check_openai(self) -> None:
    """檢查 OpenAI 服務可用性"""
    # 實作檢查邏輯

# 2. 在 discover_services 中調用
await asyncio.gather(
    self._check_ollama(),
    self._check_lmstudio(),
    self._check_openai(),  # 新增
    return_exceptions=True
)

# 完成！無需修改 UnifiedModelManager
```

## 📚 參考文檔

- [CLAUDE.md - Linus 方法論](../../CLAUDE.md)
- [MCP 配置文檔](../../mcp/config.py)
- [LLM 客戶端文檔](../../mcp/llm/client.py)

## 🏷️ 標籤

`refactoring` `technical-debt` `medium-priority` `linus-methodology` `prevention` `week-3`

## ⏱️ 預估工時

**2-3 天**

**分解：**
- Day 1: 創建 ServiceDiscovery 和 ModelCache
- Day 2: 重構 UnifiedModelManager
- Day 3: 測試 + 文檔更新
