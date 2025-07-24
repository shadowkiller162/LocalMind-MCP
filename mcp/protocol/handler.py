"""
MCP 協議處理器

實作 MCP 協議的核心處理邏輯。
"""

import json
import logging
from typing import Any, Dict, Optional, Callable, Awaitable
from asyncio import Protocol

from ..config import get_config
from ..exceptions import MCPProtocolError
from .messages import MCPMessage, MCPRequest, MCPResponse, MCPNotification
from .types import MCPMessageType, MCPConnectionState, MCPCapabilities


logger = logging.getLogger(__name__)


class MCPHandler:
    """MCP 協議處理器"""
    
    def __init__(self):
        self.config = get_config()
        self.state = MCPConnectionState.DISCONNECTED
        self.capabilities: Optional[MCPCapabilities] = None
        self._message_handlers: Dict[str, Callable] = {}
        self._setup_default_handlers()
    
    def _setup_default_handlers(self):
        """設置預設的訊息處理器"""
        self._message_handlers.update({
            "initialize": self._handle_initialize,
            "initialized": self._handle_initialized,
            "ping": self._handle_ping,
            "shutdown": self._handle_shutdown,
        })
    
    async def handle_message(self, raw_message: str) -> Optional[str]:
        """處理收到的訊息"""
        try:
            message_data = json.loads(raw_message)
            logger.debug(f"Received message: {message_data}")
            
            # 驗證訊息格式
            if not isinstance(message_data, dict):
                raise MCPProtocolError("Message must be a JSON object")
            
            if message_data.get("jsonrpc") != "2.0":
                raise MCPProtocolError("Invalid JSON-RPC version")
            
            # 判斷訊息類型並處理
            if "method" in message_data:
                if "id" in message_data:
                    # 請求訊息
                    return await self._handle_request(message_data)
                else:
                    # 通知訊息
                    await self._handle_notification(message_data)
                    return None
            elif "result" in message_data or "error" in message_data:
                # 回應訊息
                await self._handle_response(message_data)
                return None
            else:
                raise MCPProtocolError("Invalid message format")
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON message: {e}")
            return self._create_error_response(
                None, -32700, "Parse error", str(e)
            )
        except MCPProtocolError as e:
            logger.error(f"Protocol error: {e}")
            return self._create_error_response(
                message_data.get("id"), -32600, "Invalid Request", str(e)
            )
        except Exception as e:
            logger.error(f"Unexpected error handling message: {e}")
            return self._create_error_response(
                message_data.get("id"), -32603, "Internal error", str(e)
            )
    
    async def _handle_request(self, message_data: Dict[str, Any]) -> str:
        """處理請求訊息"""
        method = message_data["method"]
        message_id = message_data["id"]
        params = message_data.get("params", {})
        
        if method in self._message_handlers:
            try:
                result = await self._message_handlers[method](params)
                return self._create_success_response(message_id, result)
            except Exception as e:
                logger.error(f"Error handling method {method}: {e}")
                return self._create_error_response(
                    message_id, -32603, "Internal error", str(e)
                )
        else:
            return self._create_error_response(
                message_id, -32601, "Method not found", f"Unknown method: {method}"
            )
    
    async def _handle_notification(self, message_data: Dict[str, Any]):
        """處理通知訊息"""
        method = message_data["method"]
        params = message_data.get("params", {})
        
        if method in self._message_handlers:
            try:
                await self._message_handlers[method](params)
            except Exception as e:
                logger.error(f"Error handling notification {method}: {e}")
        else:
            logger.warning(f"Unknown notification method: {method}")
    
    async def _handle_response(self, message_data: Dict[str, Any]):
        """處理回應訊息"""
        # 這裡可以實作回應處理邏輯
        # 目前只記錄日誌
        logger.debug(f"Received response: {message_data}")
    
    async def _handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """處理初始化請求"""
        logger.info("Handling initialize request")
        
        # 驗證協議版本
        protocol_version = params.get("protocolVersion")
        if protocol_version != self.config.protocol_version:
            raise MCPProtocolError(
                f"Unsupported protocol version: {protocol_version}"
            )
        
        self.state = MCPConnectionState.CONNECTING
        
        # 返回伺服器能力
        return {
            "protocolVersion": self.config.protocol_version,
            "capabilities": {
                "experimental": {},
                "logging": {},
                "prompts": {"listChanged": True},
                "resources": {"subscribe": True, "listChanged": True},
                "tools": {"listChanged": True},
            },
            "serverInfo": {
                "name": "LocalMind-MCP",
                "version": "0.1.0",
            }
        }
    
    async def _handle_initialized(self, params: Dict[str, Any]):
        """處理初始化完成通知"""
        logger.info("Connection initialized")
        self.state = MCPConnectionState.CONNECTED
    
    async def _handle_ping(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """處理 ping 請求"""
        return {"pong": True}
    
    async def _handle_shutdown(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """處理關閉請求"""
        logger.info("Handling shutdown request")
        self.state = MCPConnectionState.DISCONNECTED
        return {}
    
    def _create_success_response(self, message_id: Any, result: Any) -> str:
        """建立成功回應"""
        response = MCPResponse(id=message_id, result=result)
        return json.dumps(response.to_dict())
    
    def _create_error_response(
        self, 
        message_id: Any, 
        code: int, 
        message: str, 
        data: Optional[Any] = None
    ) -> str:
        """建立錯誤回應"""
        error = {"code": code, "message": message}
        if data:
            error["data"] = data
        
        response = MCPResponse(id=message_id, error=error)
        return json.dumps(response.to_dict())
    
    def register_handler(self, method: str, handler: Callable):
        """註冊訊息處理器"""
        self._message_handlers[method] = handler
    
    def get_state(self) -> MCPConnectionState:
        """取得連接狀態"""
        return self.state