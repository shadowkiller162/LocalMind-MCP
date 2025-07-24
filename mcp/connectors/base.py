"""
MCP 連接器基類

定義所有 MCP 連接器的抽象基類和通用介面。
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from enum import Enum

from ..exceptions import MCPConnectorError
from ..config import get_config


class ConnectorType(Enum):
    """連接器類型"""
    FILESYSTEM = "filesystem"
    DATABASE = "database"
    API = "api"
    WEB = "web"
    GITHUB = "github"


@dataclass
class ConnectorConfig:
    """連接器配置"""
    name: str
    type: ConnectorType
    enabled: bool = True
    timeout: int = 30
    max_retries: int = 3
    config: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.config is None:
            self.config = {}


@dataclass 
class ResourceInfo:
    """資源資訊"""
    uri: str
    name: str
    description: Optional[str] = None
    mime_type: Optional[str] = None
    annotations: Optional[Dict[str, Any]] = None


@dataclass
class ToolInfo:
    """工具資訊"""
    name: str
    description: str
    input_schema: Dict[str, Any]


class BaseConnector(ABC):
    """MCP 連接器抽象基類"""
    
    def __init__(self, config: ConnectorConfig):
        self.config = config
        self.mcp_config = get_config()
        self._initialized = False
        self._resources: List[ResourceInfo] = []
        self._tools: List[ToolInfo] = []
    
    @property
    def name(self) -> str:
        """連接器名稱"""
        return self.config.name
    
    @property
    def type(self) -> ConnectorType:
        """連接器類型"""
        return self.config.type
    
    @property
    def is_enabled(self) -> bool:
        """是否啟用"""
        return self.config.enabled
    
    @property
    def is_initialized(self) -> bool:
        """是否已初始化"""
        return self._initialized
    
    @abstractmethod
    async def initialize(self) -> None:
        """初始化連接器"""
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """清理連接器資源"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """健康檢查"""
        pass
    
    # 資源相關方法
    
    async def list_resources(self) -> List[ResourceInfo]:
        """列出可用資源"""
        if not self._initialized:
            raise MCPConnectorError(
                "Connector not initialized", 
                connector_type=self.type.value
            )
        return self._resources.copy()
    
    @abstractmethod
    async def read_resource(self, uri: str) -> Dict[str, Any]:
        """讀取資源內容"""
        pass
    
    async def subscribe_to_resource(self, uri: str) -> bool:
        """訂閱資源變更"""
        # 預設實作，子類可以覆寫
        return False
    
    async def unsubscribe_from_resource(self, uri: str) -> bool:
        """取消訂閱資源變更"""
        # 預設實作，子類可以覆寫
        return False
    
    # 工具相關方法
    
    async def list_tools(self) -> List[ToolInfo]:
        """列出可用工具"""
        if not self._initialized:
            raise MCPConnectorError(
                "Connector not initialized",
                connector_type=self.type.value
            )
        return self._tools.copy()
    
    @abstractmethod
    async def call_tool(
        self, 
        name: str, 
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """呼叫工具"""
        pass
    
    # 提示相關方法（可選實作）
    
    async def list_prompts(self) -> List[Dict[str, Any]]:
        """列出可用提示"""
        return []
    
    async def get_prompt(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """取得提示內容"""
        raise MCPConnectorError(
            f"Prompt '{name}' not supported by {self.type.value} connector",
            connector_type=self.type.value
        )
    
    # 內部輔助方法
    
    def _add_resource(self, resource: ResourceInfo) -> None:
        """新增資源"""
        self._resources.append(resource)
    
    def _add_tool(self, tool: ToolInfo) -> None:
        """新增工具"""
        self._tools.append(tool)
    
    def _validate_config(self, required_keys: List[str]) -> None:
        """驗證配置項目"""
        missing_keys = [
            key for key in required_keys 
            if key not in self.config.config
        ]
        if missing_keys:
            raise MCPConnectorError(
                f"Missing required config keys: {missing_keys}",
                connector_type=self.type.value
            )
    
    async def __aenter__(self):
        """異步上下文管理器入口"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """異步上下文管理器出口"""
        await self.cleanup()
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', type='{self.type.value}')"