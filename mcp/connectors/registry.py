"""
MCP 連接器註冊表

管理所有可用的 MCP 連接器。
"""

from typing import Dict, List, Type, Optional
import logging

from .base import BaseConnector, ConnectorConfig, ConnectorType
from ..exceptions import MCPConnectorError


logger = logging.getLogger(__name__)


class ConnectorRegistry:
    """連接器註冊表"""
    
    def __init__(self):
        self._connector_classes: Dict[ConnectorType, Type[BaseConnector]] = {}
        self._active_connectors: Dict[str, BaseConnector] = {}
    
    def register_connector(
        self, 
        connector_type: ConnectorType, 
        connector_class: Type[BaseConnector]
    ) -> None:
        """註冊連接器類別"""
        if not issubclass(connector_class, BaseConnector):
            raise MCPConnectorError(
                f"Connector class must inherit from BaseConnector",
                connector_type=connector_type.value
            )
        
        self._connector_classes[connector_type] = connector_class
        logger.info(f"Registered connector: {connector_type.value}")
    
    def unregister_connector(self, connector_type: ConnectorType) -> None:
        """取消註冊連接器類別"""
        if connector_type in self._connector_classes:
            del self._connector_classes[connector_type]
            logger.info(f"Unregistered connector: {connector_type.value}")
    
    def create_connector(self, config: ConnectorConfig) -> BaseConnector:
        """建立連接器實例"""
        if config.type not in self._connector_classes:
            raise MCPConnectorError(
                f"Unknown connector type: {config.type.value}",
                connector_type=config.type.value
            )
        
        connector_class = self._connector_classes[config.type]
        connector = connector_class(config)
        
        # 如果連接器已啟用，加入活躍連接器列表
        if config.enabled:
            self._active_connectors[config.name] = connector
            logger.info(f"Created active connector: {config.name}")
        
        return connector
    
    def get_connector(self, name: str) -> Optional[BaseConnector]:
        """取得連接器實例"""
        return self._active_connectors.get(name)
    
    def get_connectors_by_type(self, connector_type: ConnectorType) -> List[BaseConnector]:
        """根據類型取得連接器"""
        return [
            connector for connector in self._active_connectors.values()
            if connector.type == connector_type
        ]
    
    def list_active_connectors(self) -> List[BaseConnector]:
        """列出所有活躍連接器"""
        return list(self._active_connectors.values())
    
    def list_registered_types(self) -> List[ConnectorType]:
        """列出所有已註冊的連接器類型"""
        return list(self._connector_classes.keys())
    
    async def initialize_all(self) -> None:
        """初始化所有活躍連接器"""
        for name, connector in self._active_connectors.items():
            try:
                if not connector.is_initialized:
                    await connector.initialize()
                    logger.info(f"Initialized connector: {name}")
            except Exception as e:
                logger.error(f"Failed to initialize connector {name}: {e}")
                # 從活躍列表中移除失敗的連接器
                if name in self._active_connectors:
                    del self._active_connectors[name]
    
    async def cleanup_all(self) -> None:
        """清理所有活躍連接器"""
        for name, connector in list(self._active_connectors.items()):
            try:
                if connector.is_initialized:
                    await connector.cleanup()
                    logger.info(f"Cleaned up connector: {name}")
            except Exception as e:
                logger.error(f"Failed to cleanup connector {name}: {e}")
            finally:
                # 從活躍列表中移除
                if name in self._active_connectors:
                    del self._active_connectors[name]
    
    async def health_check_all(self) -> Dict[str, bool]:
        """對所有連接器進行健康檢查"""
        results = {}
        for name, connector in self._active_connectors.items():
            try:
                if connector.is_initialized:
                    results[name] = await connector.health_check()
                else:
                    results[name] = False
            except Exception as e:
                logger.error(f"Health check failed for connector {name}: {e}")
                results[name] = False
        
        return results
    
    def remove_connector(self, name: str) -> bool:
        """移除連接器"""
        if name in self._active_connectors:
            del self._active_connectors[name]
            logger.info(f"Removed connector: {name}")
            return True
        return False
    
    def __len__(self) -> int:
        """返回活躍連接器數量"""
        return len(self._active_connectors)
    
    def __contains__(self, name: str) -> bool:
        """檢查是否包含指定名稱的連接器"""
        return name in self._active_connectors


# 全域連接器註冊表實例
registry = ConnectorRegistry()