from ..base import Skill


class FileReaderSkill(Skill):
    name = "file_reader"
    description = "Read contents of a file"

    @property
    def parameters(self):
        return {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}

    async def execute(self, path: str = "", **kwargs):
        from pathlib import Path as P
        fp = P(path)
        if not fp.exists():
            return {"error": "File not found"}
        return {"content": fp.read_text()[:10000]}
