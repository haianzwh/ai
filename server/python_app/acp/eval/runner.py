from __future__ import annotations
import time
from typing import Any


class Evaluator:
    """评估器抽象"""

    def __init__(self, name: str):
        self.name = name

    async def evaluate(self, input_data: Any, expected: Any = None) -> dict:
        return {"score": 0, "details": {}}


class EvalRunner:
    """评估执行器"""

    def __init__(self):
        self._evaluators: dict[str, list[Evaluator]] = {}
        self._datasets: dict[str, list[dict]] = {}

    def register(self, category: str, evaluator: Evaluator):
        self._evaluators.setdefault(category, []).append(evaluator)

    def load_dataset(self, name: str, data: list[dict]):
        self._datasets[name] = data

    async def run(self, category: str, dataset_name: str) -> dict:
        evaluators = self._evaluators.get(category, [])
        dataset = self._datasets.get(dataset_name, [])
        results = []
        for item in dataset:
            for ev in evaluators:
                t0 = time.time()
                score = await ev.evaluate(item.get("input"), item.get("expected"))
                score["latency_ms"] = (time.time() - t0) * 1000
                score["evaluator"] = ev.name
                results.append(score)
        avg = sum(r.get("score", 0) for r in results) / max(len(results), 1)
        return {"category": category, "average_score": avg, "total": len(results), "details": results}
