from __future__ import annotations
from ..protocol import ACPResponse


class HealthHandler:
    """处理 health.check 方法"""

    async def __call__(self, params: dict) -> ACPResponse:
        return ACPResponse.success({"status": "ok", "version": "2.0.0"})
