from __future__ import annotations
import importlib
from pathlib import Path
from .base import Skill
from .registry import skill_registry


def load_skills_from_dir(skills_dir: str):
    """从目录热加载用户自定义 Skill"""
    p = Path(skills_dir)
    if not p.exists():
        return
    for d in p.iterdir():
        if d.is_dir():
            skill_yaml = d / "skill.yaml"
            main_py = d / "main.py"
            if main_py.exists():
                try:
                    spec = importlib.util.spec_from_file_location(d.name, str(main_py))
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    if hasattr(mod, "skill") and isinstance(mod.skill, Skill):
                        skill_registry.register(mod.skill)
                except Exception as e:
                    print(f"[Skill] 加载失败 {d.name}: {e}")
