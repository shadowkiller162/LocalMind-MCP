"""
MCP 配置管理系統

提供 MCP 模組的配置管理功能，支援環境變數和配置檔案。
遵循 Django 專案的配置管理慣例。
"""

import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from pathlib import Path

from .exceptions import MCPConfigurationError


@dataclass
class MCPConfig:
    """MCP 模組配置類別"""
    
    # MCP 協議配置
    protocol_version: str = "1.0"
    max_connections: int = 10
    connection_timeout: int = 60
    request_timeout: int = 300
    
    # 本地 LLM 配置
    ollama_host: str = "host.docker.internal"
    ollama_port: int = 11434
    ollama_timeout: int = 300
    
    # LM Studio 配置
    lmstudio_host: str = "host.docker.internal"
    lmstudio_port: int = 1234
    lmstudio_timeout: int = 300
    
    # 預設 LLM 服務和模型
    default_llm_service: str = "auto"  # auto, ollama, lmstudio
    default_model: str = "llama2"
    
    # 連接器配置
    enabled_connectors: List[str] = field(default_factory=lambda: [
        "filesystem", "database"
    ])
    connector_timeout: int = 30
    
    # 快取配置
    enable_cache: bool = True
    cache_ttl: int = 3600  # 1 hour
    cache_max_size: int = 1000
    
    # 日誌配置
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # 安全配置
    api_key_env_prefix: str = "MCP_"
    allowed_hosts: List[str] = field(default_factory=lambda: ["localhost", "127.0.0.1"])
    
    @classmethod
    def from_env(cls) -> "MCPConfig":
        """從環境變數載入配置"""
        config = cls()
        
        # 從環境變數更新配置
        env_mapping = {
            "MCP_PROTOCOL_VERSION": ("protocol_version", str),
            "MCP_MAX_CONNECTIONS": ("max_connections", int),
            "MCP_CONNECTION_TIMEOUT": ("connection_timeout", int),
            "MCP_REQUEST_TIMEOUT": ("request_timeout", int),
            
            "MCP_OLLAMA_HOST": ("ollama_host", str),
            "MCP_OLLAMA_PORT": ("ollama_port", int),
            "MCP_OLLAMA_TIMEOUT": ("ollama_timeout", int),
            
            "MCP_LMSTUDIO_HOST": ("lmstudio_host", str),
            "MCP_LMSTUDIO_PORT": ("lmstudio_port", int),
            "MCP_LMSTUDIO_TIMEOUT": ("lmstudio_timeout", int),
            
            "MCP_DEFAULT_LLM_SERVICE": ("default_llm_service", str),
            "MCP_DEFAULT_MODEL": ("default_model", str),
            
            "MCP_CONNECTOR_TIMEOUT": ("connector_timeout", int),
            "MCP_ENABLE_CACHE": ("enable_cache", lambda x: x.lower() == "true"),
            "MCP_CACHE_TTL": ("cache_ttl", int),
            "MCP_CACHE_MAX_SIZE": ("cache_max_size", int),
            
            "MCP_LOG_LEVEL": ("log_level", str),
        }
        
        for env_key, (attr_name, type_converter) in env_mapping.items():
            if env_value := os.getenv(env_key):
                try:
                    setattr(config, attr_name, type_converter(env_value))
                except (ValueError, TypeError) as e:
                    raise MCPConfigurationError(
                        f"Invalid value for {env_key}: {env_value}",
                        config_key=env_key
                    ) from e
        
        # 處理列表類型的環境變數
        if enabled_connectors := os.getenv("MCP_ENABLED_CONNECTORS"):
            config.enabled_connectors = [
                connector.strip() 
                for connector in enabled_connectors.split(",")
            ]
        
        if allowed_hosts := os.getenv("MCP_ALLOWED_HOSTS"):
            config.allowed_hosts = [
                host.strip() 
                for host in allowed_hosts.split(",")
            ]
        
        return config
    
    @classmethod
    def from_file(cls, config_path: Path) -> "MCPConfig":
        """從配置檔案載入配置"""
        if not config_path.exists():
            raise MCPConfigurationError(
                f"Configuration file not found: {config_path}"
            )
        
        # 這裡可以根據需要實作 YAML/TOML/JSON 配置檔案讀取
        # 目前先返回預設配置
        return cls.from_env()
    
    def validate(self) -> None:
        """驗證配置的有效性"""
        errors = []
        
        # 驗證基本數值範圍
        if self.max_connections <= 0:
            errors.append("max_connections must be positive")
        
        if self.connection_timeout <= 0:
            errors.append("connection_timeout must be positive")
        
        if self.ollama_port <= 0 or self.ollama_port > 65535:
            errors.append("ollama_port must be between 1 and 65535")
        
        # 驗證日誌級別
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level not in valid_log_levels:
            errors.append(f"log_level must be one of {valid_log_levels}")
        
        # 驗證連接器名稱
        valid_connectors = ["filesystem", "database", "github", "web"]
        invalid_connectors = [
            connector for connector in self.enabled_connectors 
            if connector not in valid_connectors
        ]
        if invalid_connectors:
            errors.append(
                f"Invalid connectors: {invalid_connectors}. "
                f"Valid options: {valid_connectors}"
            )
        
        if errors:
            raise MCPConfigurationError(
                f"Configuration validation failed: {'; '.join(errors)}"
            )
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        return {
            "protocol_version": self.protocol_version,
            "max_connections": self.max_connections,
            "connection_timeout": self.connection_timeout,
            "request_timeout": self.request_timeout,
            "ollama_host": self.ollama_host,
            "ollama_port": self.ollama_port,
            "ollama_timeout": self.ollama_timeout,
            "default_model": self.default_model,
            "enabled_connectors": self.enabled_connectors,
            "connector_timeout": self.connector_timeout,
            "enable_cache": self.enable_cache,
            "cache_ttl": self.cache_ttl,
            "cache_max_size": self.cache_max_size,
            "log_level": self.log_level,
            "log_format": self.log_format,
            "api_key_env_prefix": self.api_key_env_prefix,
            "allowed_hosts": self.allowed_hosts,
        }


# 全域配置實例
_global_config: Optional[MCPConfig] = None


def get_config() -> MCPConfig:
    """取得全域 MCP 配置實例"""
    global _global_config
    if _global_config is None:
        _global_config = MCPConfig.from_env()
        _global_config.validate()
    return _global_config


def set_config(config: MCPConfig) -> None:
    """設定全域 MCP 配置實例"""
    global _global_config
    config.validate()
    _global_config = config