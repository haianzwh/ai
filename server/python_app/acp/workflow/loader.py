from pathlib import Path
from .engine import WorkflowEngine


def load_workflows_from_dir(engine: WorkflowEngine, dir_path: str):
    engine.load_dir(dir_path)
