"""
MCP LLM 類型定義

定義 LLM 整合中使用的各種類型。
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class LLMStatus(Enum):
    """LLM 狀態"""
    AVAILABLE = "available"
    LOADING = "loading"
    ERROR = "error"
    OFFLINE = "offline"


@dataclass
class ModelInfo:
    """模型資訊"""
    name: str
    size: Optional[int] = None
    digest: Optional[str] = None
    modified_at: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    status: LLMStatus = LLMStatus.AVAILABLE


@dataclass
class LLMResponse:
    """LLM 回應"""
    content: str
    model: str
    created_at: str
    done: bool = True
    total_duration: Optional[int] = None
    load_duration: Optional[int] = None
    prompt_eval_count: Optional[int] = None
    prompt_eval_duration: Optional[int] = None
    eval_count: Optional[int] = None
    eval_duration: Optional[int] = None
    context: Optional[List[int]] = None


@dataclass
class ChatMessage:
    """聊天訊息"""
    role: str  # "system", "user", "assistant"
    content: str


@dataclass
class GenerateRequest:
    """生成請求"""
    model: str
    prompt: str
    stream: bool = False
    context: Optional[List[int]] = None
    options: Optional[Dict[str, Any]] = None


@dataclass
class ChatRequest:
    """聊天請求"""
    model: str
    messages: List[ChatMessage]
    stream: bool = False
    options: Optional[Dict[str, Any]] = None