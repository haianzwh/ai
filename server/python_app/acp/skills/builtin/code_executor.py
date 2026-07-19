from ..base import Skill


class CodeExecutorSkill(Skill):
    name = "code_executor"
    description = "Execute Python code in a sandbox"

    @property
    def parameters(self):
        return {"type": "object", "properties": {"code": {"type": "string"}, "language": {"type": "string"}}, "required": ["code"]}

    async def execute(self, code: str = "", language: str = "python", **kwargs):
        if language == "python":
            import io, sys
            old_stdout = sys.stdout
            sys.stdout = buf = io.StringIO()
            try:
                exec(code, {"__builtins__": {}})
                output = buf.getvalue()
            finally:
                sys.stdout = old_stdout
            return {"output": output}
        return {"output": f"Language {language} not supported"}
