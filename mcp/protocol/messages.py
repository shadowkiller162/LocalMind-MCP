"""
MCP 協議訊息類型

定義 MCP 協議中的各種訊息格式。
"""

from typing import Any, Dict, Optional, Union
from dataclasses import dataclass
from .types import MCPMessageType


@dataclass
class MCPMessage:
    """MCP 基礎訊息類別"""
    jsonrpc: str = "2.0"
    id: Optional[Union[str, int]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        result = {"jsonrpc": self.jsonrpc}
        if self.id is not None:
            result["id"] = self.id
        return result


@dataclass
class MCPRequest(MCPMessage):
    """MCP 請求訊息"""
    method: str = ""
    params: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["method"] = self.method
        if self.params:
            result["params"] = self.params
        return result


@dataclass
class MCPResponse(MCPMessage):
    """MCP 回應訊息"""
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        if self.result is not None:
            result["result"] = self.result
        if self.error:
            result["error"] = self.error
        return result


@dataclass
class MCPNotification(MCPMessage):
    """MCP 通知訊息"""
    method: str = ""
    params: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        # 通知訊息不應該有 id
        self.id = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {"jsonrpc": self.jsonrpc, "method": self.method}
        if self.params:
            result["params"] = self.params
        return result