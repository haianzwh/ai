from __future__ import annotations
from typing import Optional
from .protocol import ACPRequest, ACPResponse, ACPMethod, ACPErrorCode
from .router import Router
from .handlers.chat import ChatHandler
from .handlers.models import ModelsHandler
from .handlers.health import HealthHandler
from .handlers.skills import SkillsHandler
from .handlers.workflow import WorkflowHandler
from .middleware.registry import plugin_registry


class ACPServer:
    """ACP 服务端 — 接收 ACPRequest，路由到 handler，返回 ACPResponse"""

    def __init__(self, external_gateway=None):
        self.external_gateway = external_gateway
        self.router = Router()
        self._handlers: dict[str, object] = {}
        self._register_default_handlers()

    def _register_default_handlers(self):
        self._handlers[ACPMethod.CHAT_COMPLETIONS] = ChatHandler(self.external_gateway)
        self._handlers[ACPMethod.MODELS_LIST] = ModelsHandler()
        self._handlers[ACPMethod.HEALTH_CHECK] = HealthHandler()
        self._handlers["skills.list"] = SkillsHandler()
        self._handlers["skills.execute"] = SkillsHandler()
        self._handlers["workflow.execute"] = WorkflowHandler()

    async def route_request(self, request: ACPRequest) -> ACPResponse:
        method = request.method
        params = request.params
        request_id = request.id

        raw = {"method": method, "params": params}

        blocked = await plugin_registry.run_on_request(method, params)
        if blocked:
            return ACPResponse.fail(ACPErrorCode.RATE_LIMIT, str(blocked.get("error", "Blocked")), request_id)

        provider_name = params.get("provider", "")

        if provider_name and self.router.is_external(provider_name):
            if not self.external_gateway:
                return ACPResponse.fail(ACPErrorCode.PROVIDER_ERROR, "External gateway not available", request_id)
            return await self.external_gateway.call(provider_name, method, params)

        handler = self._handlers.get(method)
        if not handler:
            return ACPResponse.fail(ACPErrorCode.METHOD_NOT_FOUND, f"Unknown method: {method}", request_id)

        try:
            result = await handler(params)
            if isinstance(result, ACPResponse):
                result.id = request_id
                resp = result
            else:
                resp = ACPResponse.success(result, request_id)
            resp.result = await plugin_registry.run_on_response(method, params, resp.result)
            return resp
        except Exception as e:
            return ACPResponse.fail(ACPErrorCode.INTERNAL_ERROR, str(e), request_id)

    def register_provider_routes(self, providers_config: dict):
        for pid, cfg in providers_config.items():
            ptype = cfg.get("type", "internal")
            self.router.add(pid, ptype)
