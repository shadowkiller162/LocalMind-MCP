"""
MCP 模組自定義例外類別

定義 MCP 模組中使用的各種例外情況，提供清晰的錯誤分類和處理機制。
"""

from typing import Optional, Any, Dict


class MCPError(Exception):
    """MCP 模組基礎例外類別"""
    
    def __init__(
        self, 
        message: str, 
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
    
    def __str__(self) -> str:
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class MCPConnectionError(MCPError):
    """MCP 連接相關錯誤"""
    
    def __init__(
        self, 
        message: str, 
        connection_type: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, error_code="MCP_CONNECTION_ERROR", **kwargs)
        self.connection_type = connection_type


class MCPProtocolError(MCPError):
    """MCP 協議相關錯誤"""
    
    def __init__(
        self, 
        message: str, 
        protocol_version: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, error_code="MCP_PROTOCOL_ERROR", **kwargs)
        self.protocol_version = protocol_version


class MCPConfigurationError(MCPError):
    """MCP 配置相關錯誤"""
    
    def __init__(self, message: str, config_key: Optional[str] = None, **kwargs):
        super().__init__(message, error_code="MCP_CONFIG_ERROR", **kwargs)
        self.config_key = config_key


class MCPConnectorError(MCPError):
    """MCP 連接器相關錯誤"""
    
    def __init__(
        self, 
        message: str, 
        connector_type: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, error_code="MCP_CONNECTOR_ERROR", **kwargs)
        self.connector_type = connector_type


class MCPLLMError(MCPError):
    """MCP LLM 整合相關錯誤"""
    
    def __init__(
        self, 
        message: str, 
        llm_type: Optional[str] = None,
        model_name: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, error_code="MCP_LLM_ERROR", **kwargs)
        self.llm_type = llm_type
        self.model_name = model_name