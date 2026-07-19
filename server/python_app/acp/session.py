from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ACPSession:
    session_id: str = field(default_factory=lambda: f"acp_{uuid.uuid4().hex[:12]}")
    provider: str = ""
    model: str = ""
    messages: list[dict] = field(default_factory=list)

    def add_message(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})


class ACPSessionManager:
    """ACP 会话管理（多轮对话上下文）"""

    def __init__(self):
        self._sessions: dict[str, ACPSession] = {}

    def create(self, provider: str = "", model: str = "") -> ACPSession:
        s = ACPSession(provider=provider, model=model)
        self._sessions[s.session_id] = s
        return s

    def get(self, session_id: str) -> Optional[ACPSession]:
        return self._sessions.get(session_id)

    def update(self, session_id: str, **kwargs):
        s = self._sessions.get(session_id)
        if s:
            for k, v in kwargs.items():
                if hasattr(s, k):
                    setattr(s, k, v)

    def remove(self, session_id: str):
        self._sessions.pop(session_id, None)
