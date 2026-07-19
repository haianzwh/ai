from __future__ import annotations
from ..protocol import ACPResponse, ACPErrorCode
from ..workflow.engine import WorkflowEngine


_engine: WorkflowEngine = None


def set_workflow_engine(engine: WorkflowEngine):
    global _engine
    _engine = engine


class WorkflowHandler:
    """处理 workflow.execute 方法"""

    async def __call__(self, params: dict) -> ACPResponse:
        if not _engine:
            return ACPResponse.fail(ACPErrorCode.INTERNAL_ERROR, "Workflow engine not initialized")
        name = params.get("workflow", "")
        if not name:
            return ACPResponse.fail(ACPErrorCode.INVALID_PARAMS, "workflow name required")
        try:
            result = await _engine.execute(name, **params.get("args", {}))
            return ACPResponse.success(result)
        except Exception as e:
            return ACPResponse.fail(ACPErrorCode.INTERNAL_ERROR, str(e))
