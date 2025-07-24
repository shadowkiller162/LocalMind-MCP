"""
MCP 配置系統測試

測試 MCP 模組的配置管理功能。
"""

import os
import pytest
from unittest.mock import patch

from mcp.config import MCPConfig, get_config, set_config
from mcp.exceptions import MCPConfigurationError


class TestMCPConfig:
    """MCP 配置類別測試"""
    
    def test_default_config(self):
        """測試預設配置值"""
        config = MCPConfig()
        
        assert config.protocol_version == "1.0"
        assert config.max_connections == 10
        assert config.ollama_host == "localhost"
        assert config.ollama_port == 11434
        assert config.enabled_connectors == ["filesystem", "database"]
        assert config.enable_cache is True
        assert config.log_level == "INFO"
    
    def test_from_env(self):
        """測試從環境變數載入配置"""
        env_vars = {
            "MCP_PROTOCOL_VERSION": "2.0",
            "MCP_MAX_CONNECTIONS": "20",
            "MCP_OLLAMA_HOST": "remote-host",
            "MCP_OLLAMA_PORT": "8080",
            "MCP_ENABLED_CONNECTORS": "filesystem,github,database",
            "MCP_LOG_LEVEL": "DEBUG",
        }
        
        with patch.dict(os.environ, env_vars):
            config = MCPConfig.from_env()
            
            assert config.protocol_version == "2.0"
            assert config.max_connections == 20
            assert config.ollama_host == "remote-host"
            assert config.ollama_port == 8080
            assert config.enabled_connectors == ["filesystem", "github", "database"]
            assert config.log_level == "DEBUG"
    
    def test_from_env_invalid_values(self):
        """測試環境變數無效值的處理"""
        with patch.dict(os.environ, {"MCP_MAX_CONNECTIONS": "invalid"}):
            with pytest.raises(MCPConfigurationError) as exc_info:
                MCPConfig.from_env()
            
            assert "Invalid value for MCP_MAX_CONNECTIONS" in str(exc_info.value)
    
    def test_validate_success(self):
        """測試配置驗證成功"""
        config = MCPConfig()
        # 應該不會拋出例外
        config.validate()
    
    def test_validate_invalid_max_connections(self):
        """測試無效的最大連接數"""
        config = MCPConfig(max_connections=0)
        
        with pytest.raises(MCPConfigurationError) as exc_info:
            config.validate()
        
        assert "max_connections must be positive" in str(exc_info.value)
    
    def test_validate_invalid_port(self):
        """測試無效的端口號"""
        config = MCPConfig(ollama_port=70000)
        
        with pytest.raises(MCPConfigurationError) as exc_info:
            config.validate()
        
        assert "ollama_port must be between 1 and 65535" in str(exc_info.value)
    
    def test_validate_invalid_log_level(self):
        """測試無效的日誌級別"""
        config = MCPConfig(log_level="INVALID")
        
        with pytest.raises(MCPConfigurationError) as exc_info:
            config.validate()
        
        assert "log_level must be one of" in str(exc_info.value)
    
    def test_validate_invalid_connectors(self):
        """測試無效的連接器名稱"""
        config = MCPConfig(enabled_connectors=["filesystem", "invalid_connector"])
        
        with pytest.raises(MCPConfigurationError) as exc_info:
            config.validate()
        
        assert "Invalid connectors" in str(exc_info.value)
    
    def test_to_dict(self):
        """測試轉換為字典格式"""
        config = MCPConfig()
        config_dict = config.to_dict()
        
        assert isinstance(config_dict, dict)
        assert config_dict["protocol_version"] == "1.0"
        assert config_dict["max_connections"] == 10
        assert config_dict["enabled_connectors"] == ["filesystem", "database"]


class TestGlobalConfig:
    """全域配置函數測試"""
    
    def test_get_config_singleton(self):
        """測試全域配置的單例模式"""
        # 清除全域配置
        import mcp.config
        mcp.config._global_config = None
        
        config1 = get_config()
        config2 = get_config()
        
        # 應該是同一個實例
        assert config1 is config2
    
    def test_set_config(self):
        """測試設定全域配置"""
        custom_config = MCPConfig(protocol_version="2.0")
        set_config(custom_config)
        
        retrieved_config = get_config()
        assert retrieved_config.protocol_version == "2.0"
    
    def test_set_invalid_config(self):
        """測試設定無效配置"""
        invalid_config = MCPConfig(max_connections=0)
        
        with pytest.raises(MCPConfigurationError):
            set_config(invalid_config)