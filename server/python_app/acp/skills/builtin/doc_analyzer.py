from python_app.acp.skills.base import Skill
from pathlib import Path
import re
from collections import Counter


class DocumentAnalysisSkill(Skill):
    name = "doc_analyzer"
    description = "读产品文档/技术文档，自动总结分析：提取目录、关键特性、API 概览、变更记录"

    @property
    def parameters(self):
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "文档路径（本地 Markdown / TXT / MDX）"},
                "mode": {
                    "type": "string",
                    "enum": ["auto", "summary", "changelog", "api", "glossary"],
                    "description": "分析模式：auto=全分析 summary=摘要 changelog=变更 api=接口 glossary=术语",
                },
            },
            "required": ["path"],
        }

    async def execute(self, path: str = "", mode: str = "auto", **kwargs):
        fp = Path(path)
        if not fp.exists():
            return {"error": f"文件不存在: {path}"}

        text = fp.read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines()

        result = {"file": path, "size": len(text), "lines": len(lines)}

        if mode in ("auto", "summary"):
            result["summary"] = self._summarize(text, lines)
        if mode in ("auto", "changelog"):
            result["changelog"] = self._extract_changelog(lines)
        if mode in ("auto", "api"):
            result["api"] = self._extract_api(lines)
        if mode == "glossary":
            result["glossary"] = self._extract_glossary(text)
        if mode == "auto":
            result["toc"] = self._extract_toc(lines)
            result["keywords"] = self._extract_keywords(text)

        return result

    def _extract_toc(self, lines):
        toc = []
        for i, line in enumerate(lines):
            m = re.match(r"^(#{1,6})\s+(.+)$", line.strip())
            if m:
                toc.append({"level": len(m.group(1)), "title": m.group(2).strip(), "line": i + 1})
        return toc

    def _summarize(self, text, lines):
        first_h1 = None
        for line in lines:
            m = re.match(r"^#\s+(.+)$", line.strip())
            if m:
                first_h1 = m.group(1).strip()
                break
        sections = re.findall(r"^##\s+(.+)$", text, re.MULTILINE)
        word_count = len(text.split())
        return {
            "title": first_h1 or Path(self.name).stem,
            "sections": sections[:20],
            "section_count": len(sections),
            "word_count": word_count,
            "estimated_read_time": max(1, word_count // 200),
        }

    def _extract_changelog(self, lines):
        changelog = []
        in_log = False
        for line in lines:
            if re.match(r"^#{1,3}\s*(变更|更新|Changelog|Release Notes|版本)", line, re.I):
                in_log = True
            elif in_log and re.match(r"^#{1,3}\s+", line):
                break
            elif in_log and line.strip():
                changelog.append(line.strip())
        return changelog[:50]

    def _extract_api(self, lines):
        apis = []
        current_section = ""
        for line in lines:
            m = re.match(r"^##+\s+(.+)$", line.strip())
            if m:
                current_section = m.group(1).strip()
            am = re.match(
                r"`?(GET|POST|PUT|DELETE|PATCH)\s+(/\S+)`?\s*[-–—]?\s*(.*)",
                line.strip(),
                re.I,
            )
            if am:
                apis.append({"method": am.group(1).upper(), "path": am.group(2), "desc": am.group(3), "section": current_section})
            fm = re.match(r"^[-*]\s*`?(\w+)[(]`,?\s*(.*)", line.strip())
            if fm:
                apis.append({"function": fm.group(1), "desc": fm.group(2), "section": current_section})
        return apis[:30]

    def _extract_glossary(self, text):
        pairs = re.findall(r"^[-*]\s*\*{0,2}([A-Z][A-Za-z0-9_\- ]+)\*{0,2}\s*[：:]\s*(.+)$", text, re.MULTILINE)
        return [{"term": t.strip(), "definition": d.strip()} for t, d in pairs[:30]]

    def _extract_keywords(self, text):
        words = re.findall(r"\b[A-Z][a-z]{2,}(?:[A-Z][a-z]+)*\b", text)
        return [w for w, _ in Counter(words).most_common(20)]
