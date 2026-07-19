from ..base import Skill


class CalculatorSkill(Skill):
    name = "calculator"
    description = "Evaluate a mathematical expression"

    @property
    def parameters(self):
        return {"type": "object", "properties": {"expression": {"type": "string"}}, "required": ["expression"]}

    async def execute(self, expression: str = "", **kwargs):
        result = eval(expression, {"__builtins__": {}}, {})
        return {"expression": expression, "result": result}
