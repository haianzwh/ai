from __future__ import annotations
import yaml
from pathlib import Path
from typing import Any


class WorkflowEngine:
    """工作流执行引擎 — 支持 YAML 定义 + 节点编排"""

    def __init__(self, skill_registry=None, plugin_registry=None):
        self._workflows: dict[str, dict] = {}
        self._skill_registry = skill_registry
        self._plugin_registry = plugin_registry

    def load_yaml(self, path: str):
        p = Path(path)
        if p.exists():
            with open(p) as f:
                config = yaml.safe_load(f) or {}
                for name, wf in config.get("workflows", {}).items():
                    self._workflows[name] = wf
                    print(f"[Workflow] 加载: {name}")

    def load_dir(self, dir_path: str):
        d = Path(dir_path)
        if not d.exists():
            return
        for f in d.glob("*.yaml"):
            self.load_yaml(str(f))

    async def execute(self, name: str, **kwargs) -> dict:
        wf = self._workflows.get(name)
        if not wf:
            return {"success": False, "error": f"Workflow not found: {name}"}
        results = []
        for node in wf.get("nodes", []):
            node_result = await self._run_node(node, kwcontext=kwargs, results=results)
            results.append(node_result)
        return {"success": True, "results": results}

    async def _run_node(self, node: dict, **ctx) -> dict:
        ntype = node.get("type", "llm")
        if ntype == "skill" and self._skill_registry:
            skill_name = node.get("skill", "")
            args = node.get("args", {})
            return await self._skill_registry.execute(skill_name, **args)
        elif ntype == "http":
            import httpx
            async with httpx.AsyncClient() as c:
                r = await c.request(node.get("method", "GET"), node.get("url", ""))
                return {"status": r.status_code, "body": r.text[:500]}
        return {"node": node.get("name", ""), "status": "ok"}
