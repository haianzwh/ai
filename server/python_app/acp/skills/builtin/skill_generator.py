from python_app.acp.skills.base import Skill
from pathlib import Path
import re, keyword as kw_mod


class SkillGeneratorSkill(Skill):
    name = "skill_generator"
    description = "根据自然语言需求描述，自动生成可用的 Skill Python 文件，放入 hot-load 目录立即生效"

    @property
    def parameters(self):
        return {
            "type": "object",
            "properties": {
                "requirement": {
                    "type": "string",
                    "description": "需求描述，例如：'从 MySQL 查询用户订单并按金额排序，返回 JSON'",
                },
                "skill_name": {
                    "type": "string",
                    "description": "可选，自定义 Skill 名称（小写+下划线），默认自动生成",
                },
            },
            "required": ["requirement"],
        }

    async def execute(self, requirement: str = "", skill_name: str = "", **kwargs):
        if not requirement:
            return {"error": "请提供需求描述"}

        name = self._make_name(requirement, skill_name)
        class_name = "".join(part.capitalize() for part in name.split("_")) + "Skill"

        desc = self._extract_description(requirement)
        params = self._infer_params(requirement)
        imports = self._infer_imports(requirement)

        code = self._generate_code(class_name, name, desc, params, imports)

        skills_dir = Path(__file__).parent.parent.parent.parent.parent / "skills"
        skills_dir.mkdir(parents=True, exist_ok=True)
        skill_dir = skills_dir / name
        skill_dir.mkdir(exist_ok=True)

        py_path = skill_dir / "main.py"
        yaml_path = skill_dir / "skill.yaml"

        py_path.write_text(code, encoding="utf-8")
        yaml_path.write_text(
            f"name: {name}\ndescription: {desc}\nversion: \"1.0\"\n",
            encoding="utf-8",
        )

        try:
            import importlib
            spec = importlib.util.spec_from_file_location(name, str(py_path))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            if hasattr(mod, "skill") and isinstance(mod.skill, Skill):
                from python_app.acp.skills.registry import skill_registry
                skill_registry.register(mod.skill)
        except Exception as e:
            return {
                "success": True,
                "skill_name": name,
                "file": str(py_path),
                "warning": f"代码已生成，但热加载失败: {e}，重启后生效",
                "code": code,
            }

        return {
            "success": True,
            "skill_name": name,
            "description": desc,
            "file": str(py_path),
            "code": code,
        }

    def _make_name(self, req: str, hint: str = "") -> str:
        if hint:
            hint = re.sub(r"[^a-zA-Z0-9_]", "_", hint).lower().strip("_")
            if hint:
                return hint
        words = re.findall(r"[a-zA-Z\u4e00-\u9fff]+", req)
        key = [w for w in words if w.lower() not in ("一个", "的", "可以", "需要", "把", "将", "给")]
        if not key:
            key = ["custom_skill"]
        return "_".join(key[:4]).lower().replace(" ", "_")

    def _extract_description(self, req: str) -> str:
        desc = req.strip().lstrip("一个的可以需要把将给").strip()[:120]
        return desc if desc else "自动生成的自定义 Skill"

    def _infer_params(self, req: str) -> dict:
        props = {}
        required = []

        patterns = [
            (r"(?:读取|打开|文件|路径|path)\S*", "path", "string", "文件路径"),
            (r"(?:查询|搜索|查找|search|query)\S*", "query", "string", "查询关键词"),
            (r"(?:输入|内容|文字|text|content)\S*", "text", "string", "输入内容"),
            (r"(?:URL|链接|地址|网址)\S*", "url", "string", "URL 地址"),
            (r"(?:API|接口|endpoint)\S*", "endpoint", "string", "API 端点"),
            (r"(?:邮箱|email|邮件)\S*", "email", "string", "邮箱地址"),
            (r"(?:数字|数量|count|limit)\S*", "limit", "integer", "数量限制"),
        ]

        for pat, pname, ptype, pdesc in patterns:
            if re.search(pat, req, re.I):
                props[pname] = {"type": ptype, "description": pdesc}
                required.append(pname)

        if not props:
            props["input"] = {"type": "string", "description": "输入参数"}
            required = ["input"]

        return {"type": "object", "properties": props, "required": required[:5]}

    def _infer_imports(self, req: str) -> list[str]:
        imports = ["from python_app.acp.skills.base import Skill"]
        if re.search(r"(?:json|JSON)", req, re.I):
            imports.append("import json")
        if re.search(r"(?:httpx|http|请求|API|接口|fetch|crawl)", req, re.I):
            imports.append("import httpx")
        if re.search(r"(?:csv|excel)", req, re.I):
            imports.append("import csv")
        if re.search(r"(?:re|正则|regex|pattern)", req, re.I):
            imports.append("import re")
        if re.search(r"(?:db|数据库|mysql|sqlite|postgres|查询)", req, re.I):
            imports.append("import aiosqlite")
        if re.search(r"(?:path|路径|file|文件)", req, re.I):
            imports.append("from pathlib import Path")
        return imports

    def _generate_code(self, cls_name: str, name: str, desc: str, params: dict, imports: list[str]) -> str:
        import_lines = "\n".join(sorted(set(imports)))
        params_json = __import__("json").dumps(params, ensure_ascii=False, indent=4)

        return f'''{import_lines}


class {cls_name}(Skill):
    name = "{name}"
    description = "{desc}"

    @property
    def parameters(self):
        return {params_json}

    async def execute(self, **kwargs):
        # TODO: 在此实现你的业务逻辑
        # kwargs 包含用户在 parameters 中定义的参数
        result = {{
            "message": f"Skill {name} 已执行",
            "params": kwargs,
        }}
        return result


skill = {cls_name}()
'''
