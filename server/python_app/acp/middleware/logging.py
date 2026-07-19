from __future__ import annotations
import time
import logging
from .base import Plugin

logger = logging.getLogger("acp")


class LoggingMiddleware(Plugin):
    """ACP 请求日志中间件"""
    name = "logging"
    priority = 10

    async def on_request(self, method: str, params: dict) -> dict | None:
        t0 = time.time()
        provider = params.get("provider", "?")
        request_id = id(params)
        params["_log_start"] = t0
        return None

    async def on_response(self, method: str, params: dict, result):
        t0 = params.pop("_log_start", time.time())
        elapsed = (time.time() - t0) * 1000
        provider = params.get("provider", "?")
        logger.info(f"[ACP] {method} provider={provider} {elapsed:.0f}ms")
        return result
