from __future__ import annotations
import importlib
from pathlib import Path
from typing import Optional
import yaml

from .base import Provider, ProviderModel


class ProviderRegistry:
    """Provider 注册中心。支持代码注册和基于配置的热加载"""

    def __init__(self):
        self._providers: dict[str, type[Provider]] = {}
        self._config: dict = {}
        self._loaded: dict[str, Provider] = {}

    # ── 注册 ────────────────────────────────────────────

    def register(self, cls: type[Provider]):
        """通过代码注册 Provider 类"""
        inst = cls()
        pid = inst.provider_id
        self._providers[pid] = cls
        self._loaded[pid] = inst
        print(f"[Provider] 注册: {pid}")

    # ── 从 YAML 配置加载 ─────────────────────────────────

    def load_config(self, config_path: str | Path):
        """从 providers.yaml 加载配置并初始化 provider 实例"""
        path = Path(config_path)
        if not path.exists():
            print(f"[Provider] 配置不存在: {path}")
            return

        with open(path) as f:
            self._config = yaml.safe_load(f) or {}

        for pid, cfg in self._config.get("providers", {}).items():
            if pid in self._loaded:
                continue
            try:
                mod = importlib.import_module(cfg["module"])
                cls = getattr(mod, cfg["class"])
                inst = cls(cfg) if hasattr(cls, "__init__") and cls.__init__ is not object.__init__ else cls()
                self._providers[pid] = cls
                self._loaded[pid] = inst
                print(f"[Provider] 热加载: {pid} → {cfg['module']}.{cfg['class']}")
            except Exception as e:
                print(f"[Provider] 加载失败 {pid}: {e}")

    # ── 查询 ────────────────────────────────────────────

    def get(self, provider_id: str) -> Optional[Provider]:
        return self._loaded.get(provider_id)

    def list(self) -> list[tuple[str, Provider]]:
        return [(pid, inst) for pid, inst in self._loaded.items()]

    def get_config(self, provider_id: str) -> dict:
        return (self._config.get("providers", {}) or {}).get(provider_id, {})

    def list_provider_info(self) -> list[dict]:
        """返回前端需要的 provider 信息"""
        result = []
        cfg_data = (self._config.get("providers", {}) or {})
        for pid, inst in self._loaded.items():
            cfg = cfg_data.get(pid, {})
            info = {
                "id": pid,
                "label": cfg.get("label", pid),
                "icon": cfg.get("icon", "🤖"),
                "requires_key": cfg.get("requires_key", False),
                "type": cfg.get("type", "internal"),
                "has_sub_providers": bool(cfg.get("sub_providers")),
                "sub_providers": [],
            }
            if cfg.get("sub_providers"):
                info["sub_providers"] = [
                    {
                        "key": sk,
                        "label": sv.get("label", sk),
                        "key_type": sv.get("key_type", sk),
                    }
                    for sk, sv in cfg["sub_providers"].items()
                ]
            result.append(info)
        return result

    async def list_models(self, user_keys: dict[str, str] = None) -> list[dict]:
        """列出所有 user 当前可用的模型，扁平化为前端需要的格式"""
        models = []
        for pid, inst in self._loaded.items():
            cfg = self.get_config(pid)
            # 非 required_key 的 provider 直接返回模型
            if not cfg.get("requires_key"):
                try:
                    provider_models = await inst.fetch_models()
                    for pm in provider_models:
                        models.append({
                            "id": pm.id,
                            "name": pm.name,
                            "provider": pm.provider_id,
                        })
                except Exception:
                    pass
            else:
                # 需要 key 的 provider: 有 key（用户key或默认key）才显示模型
                sub_providers = cfg.get("sub_providers", {})
                has_main_key = user_keys and user_keys.get(pid)
                has_default_key = bool(cfg.get("default_key"))
                for sub_key, sub_cfg in sub_providers.items():
                    kt = sub_cfg.get("key_type", sub_key)
                    if user_keys and user_keys.get(kt):
                        label_suffix = sub_cfg.get("label", sub_key)
                        for m in cfg.get("models", []):
                            models.append({
                                "id": m["id"],
                                "name": f'{m["name"]} ({label_suffix})',
                                "provider": pid,
                                "sub_key": sub_key,
                            })
                    elif has_main_key or has_default_key:
                        label_suffix = sub_cfg.get("label", sub_key)
                        for m in cfg.get("models", []):
                            models.append({
                                "id": m["id"],
                                "name": f'{m["name"]} ({label_suffix})',
                                "provider": pid,
                                "sub_key": sub_key,
                            })
        return models


# 全局单例
registry = ProviderRegistry()
