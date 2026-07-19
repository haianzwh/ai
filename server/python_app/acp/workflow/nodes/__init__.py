# Workflow node base
from ..base import Workflow as _Wf

class SkillNode:
    def __init__(self, skill_name: str, args: dict = None):
        self.skill_name = skill_name
        self.args = args or {}

class LLMNode:
    def __init__(self, model: str, prompt: str):
        self.model = model
        self.prompt = prompt

class ConditionNode:
    def __init__(self, expression: str, true_branch: list, false_branch: list = None):
        self.expression = expression
        self.true_branch = true_branch
        self.false_branch = false_branch or []

class LoopNode:
    def __init__(self, times: int, body: list):
        self.times = times
        self.body = body

class ParallelNode:
    def __init__(self, branches: list):
        self.branches = branches

class HTTPNode:
    def __init__(self, url: str, method: str = "GET", headers: dict = None, body: str = ""):
        self.url = url
        self.method = method
        self.headers = headers or {}
        self.body = body
