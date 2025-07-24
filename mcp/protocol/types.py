"""
MCP 協議類型定義

定義 MCP 協議中使用的各種類型和枚舉。
"""

from enum import Enum
from typing import Any, Dict, Optional
from dataclasses import dataclass


class MCPMessageType(Enum):
    """MCP 訊息類型"""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    ERROR = "error"


class MCPConnectionState(Enum):
    """MCP 連接狀態"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


@dataclass
class MCPCapabilities:
    """MCP 能力描述"""
    experimental: Dict[str, Any]
    logging: Optional[Dict[str, Any]] = None
    prompts: Optional[Dict[str, Any]] = None
    resources: Optional[Dict[str, Any]] = None
    tools: Optional[Dict[str, Any]] = None