"""
MCP (Model Context Protocol) 整合模組

此模組提供 MCP 協議的完整實作，包括：
- MCP 協議處理器
- 各種資料源連接器
- 本地 LLM 整合
- 配置管理系統

主要組件：
- protocol: MCP 協議處理
- connectors: 資料源連接器
- llm: 本地 LLM 整合
- config: 配置管理
"""

__version__ = "0.1.0"
__author__ = "LocalMind-MCP Team"

# 模組級別的導入
from .config import MCPConfig
from .exceptions import MCPError, MCPConnectionError, MCPProtocolError

__all__ = [
    "MCPConfig",
    "MCPError", 
    "MCPConnectionError",
    "MCPProtocolError",
]