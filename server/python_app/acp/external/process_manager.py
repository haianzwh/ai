from __future__ import annotations
import asyncio
import signal
from typing import Optional


class ProcessManager:
    """管理外部 ACP Agent 子进程的生命周期"""

    def __init__(self):
        self._processes: dict[str, asyncio.subprocess.Process] = {}

    def register(self, name: str, process: asyncio.subprocess.Process):
        self._processes[name] = process

    async def terminate(self, name: str):
        p = self._processes.pop(name, None)
        if p and p.returncode is None:
            try:
                p.terminate()
                await p.wait()
            except Exception:
                pass

    async def shutdown_all(self):
        for name in list(self._processes.keys()):
            await self.terminate(name)
