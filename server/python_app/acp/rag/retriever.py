from __future__ import annotations
import abc
from typing import Any


class BaseRAG(abc.ABC):
    """RAG 抽象接口"""

    @abc.abstractmethod
    async def index(self, documents: list[dict]):
        ...

    @abc.abstractmethod
    async def retrieve(self, query: str, top_k: int = 5) -> list[dict]:
        ...

    @abc.abstractmethod
    async def delete(self, doc_id: str):
        ...


class SimpleRAG(BaseRAG):
    """简化版 RAG — 基于关键词匹配，可替换为向量检索"""

    def __init__(self):
        self._docs: list[dict] = []

    async def index(self, documents: list[dict]):
        for doc in documents:
            doc["_id"] = str(len(self._docs))
            self._docs.append(doc)
        print(f"[RAG] 已索引 {len(documents)} 个文档")

    async def retrieve(self, query: str, top_k: int = 5) -> list[dict]:
        keywords = set(query.lower().split())
        scored = []
        for doc in self._docs:
            score = sum(1 for kw in keywords if kw in doc.get("content", "").lower())
            if score > 0:
                scored.append((score, doc))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [doc for _, doc in scored[:top_k]]

    async def delete(self, doc_id: str):
        self._docs = [d for d in self._docs if d.get("_id") != doc_id]


class Retriever:
    """检索器"""
    def __init__(self, rag: BaseRAG):
        self.rag = rag

    async def search(self, query: str, top_k: int = 5) -> list[dict]:
        return await self.rag.retrieve(query, top_k)


class Chunker:
    """文档分块器"""
    @staticmethod
    def chunk(text: str, size: int = 500, overlap: int = 50) -> list[dict]:
        chunks = []
        for i in range(0, len(text), size - overlap):
            chunk = text[i:i + size]
            chunks.append({"content": chunk, "index": len(chunks)})
        return chunks
