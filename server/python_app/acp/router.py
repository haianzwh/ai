from __future__ import annotations
from typing import Literal

RouteType = Literal["internal", "external"]


class Router:
    """管理 Provider → 路由类型（internal / external）的映射"""

    def __init__(self):
        self._routes: dict[str, RouteType] = {}

    def add(self, provider_id: str, route_type: RouteType):
        self._routes[provider_id] = route_type

    def get(self, provider_id: str) -> RouteType:
        return self._routes.get(provider_id, "internal")

    def is_external(self, provider_id: str) -> bool:
        return self.get(provider_id) == "external"
