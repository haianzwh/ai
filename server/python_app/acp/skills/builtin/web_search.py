from ..base import Skill


class WebSearchSkill(Skill):
    name = "web_search"
    description = "Search the web for information"

    @property
    def parameters(self):
        return {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}

    async def execute(self, query: str = "", **kwargs):
        return {"results": [{"title": "Result", "snippet": f"Search result for: {query}"}]}
