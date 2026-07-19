from __future__ import annotations
from enum import IntEnum
from dataclasses import dataclass, field
from typing import Any, Optional


class ACPErrorCode(IntEnum):
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    PROVIDER_ERROR = -32000
    RATE_LIMIT = -32001
    AUTH_ERROR = -32002


class ACPMethod:
    CHAT_COMPLETIONS = "chat.completions"
    MODELS_LIST = "models.list"
    HEALTH_CHECK = "health.check"
    TOOLS_CALL = "tools.call"


@dataclass
class ACPRequest:
    jsonrpc: str = "2.0"
    method: str = ""
    params: dict = field(default_factory=dict)
    id: Optional[int] = None


@dataclass
class ACPResponse:
    jsonrpc: str = "2.0"
    result: Any = None
    error: Optional[dict] = None
    id: Optional[int] = None

    @classmethod
    def success(cls, result: Any, request_id: Optional[int] = None) -> ACPResponse:
        return cls(jsonrpc="2.0", result=result, id=request_id)

    @classmethod
    def fail(cls, code: int, message: str, request_id: Optional[int] = None) -> ACPResponse:
        return cls(jsonrpc="2.0", error={"code": code, "message": message}, id=request_id)
