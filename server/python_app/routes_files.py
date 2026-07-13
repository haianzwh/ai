"""
=============================================================================
  文件下载路由
  单文件下载 / 按项目打包下载 / 一键下载最新文件
=============================================================================
"""
import subprocess
import shutil
from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from .auth import get_current_user
from .config import ALLOWED_DIRS, FILE_DIR, OPENCODE_BASE_URL, MAX_FILES

router = APIRouter(prefix="/api", tags=["下载"])


def _is_path_allowed(target: str) -> bool:
    """检查文件路径是否在白名单目录内（防路径遍历攻击）"""
    resolved = Path(target).resolve()
    return any(resolved.is_relative_to(d) for d in ALLOWED_DIRS)


def _cleanup_file(filepath: Path) -> None:
    """后台清理临时文件"""
    try:
        filepath.unlink(missing_ok=True)
    except Exception:
        pass


@router.get("/download/file")
async def download_file(
    path: str = Query(..., description="文件绝对路径"),
    user: dict = Depends(get_current_user),
):
    """
    下载单个文件。
    
    安全策略：
    1. 路径必须在白名单目录内（/tmp/opencode, /home/ubuntu）
    2. 只有文件可被下载（目录不可）
    3. 使用 FileResponse 流式传输，浏览器触发下载
    """
    fp = path.strip()
    if not fp:
        raise HTTPException(status_code=400, detail={"error": "请提供文件路径"})
    if not _is_path_allowed(fp):
        raise HTTPException(status_code=403, detail={"error": "不允许的路径"})

    fpath = Path(fp)
    if not fpath.exists():
        raise HTTPException(status_code=404, detail={"error": "文件不存在"})
    if not fpath.is_file():
        raise HTTPException(status_code=400, detail={"error": "不是文件"})

    # FileResponse: 自动设置 Content-Type 和 Content-Disposition
    return FileResponse(
        path=str(fpath),
        filename=fpath.name,
        media_type="application/octet-stream",
    )


@router.get("/download/project/{project_id}")
async def download_project(
    project_id: str,
    user: dict = Depends(get_current_user),
):
    """
    按项目打包下载（tar.gz 压缩包）。
    
    流程：
    1. 找到项目专属目录 generated_files/<id前8位>/
    2. tar 打包所有文件
    3. 流式传输，传输完成后自动删除临时文件
    """
    short_id = project_id[:8]
    project_dir = FILE_DIR / short_id

    if not project_dir.exists() or not any(project_dir.iterdir()):
        raise HTTPException(status_code=404, detail={"error": "项目无文件"})

    # 打包（子进程执行 tar）
    tar_path = Path(f"/tmp/project-{short_id}.tar.gz")
    result = subprocess.run(
        ["tar", "-czf", str(tar_path), "-C", str(project_dir), "."],
        capture_output=True, timeout=10,
    )
    if result.returncode != 0 or not tar_path.exists() or tar_path.stat().st_size < 100:
        _cleanup_file(tar_path)
        raise HTTPException(status_code=404, detail={"error": "无文件"})

    return FileResponse(
        path=str(tar_path),
        filename=f"project-{short_id}.tar.gz",
        media_type="application/gzip",
        background=BackgroundTask(_cleanup_file, tar_path),  # 传输后自动删除
    )


@router.get("/download/latest")
async def download_latest(user: dict = Depends(get_current_user)):
    """
    一键下载最新生成文件。
    
    打包 /tmp/opencode 下所有生成文件（排除源代码和配置文件），
    只收录比 ai-chat 项目更新的文件。
    """
    tar_path = Path("/tmp/latest-generated.tar.gz")
    result = subprocess.run(
        [
            "tar", "-czf", str(tar_path),
            "-C", "/tmp/opencode",
            "--exclude=ai-chat",
            "--exclude=node_modules",
            "--exclude=.git",
            "--exclude=*.log",
            "--exclude=*.lock",
            "--exclude=*.js",
            "--exclude=*.mjs",
            "--exclude=*.json",
            "--newer", "/tmp/opencode/ai-chat/login.html",
            ".",
        ],
        capture_output=True, timeout=10,
    )
    if result.returncode != 0 or not tar_path.exists() or tar_path.stat().st_size < 100:
        _cleanup_file(tar_path)
        raise HTTPException(status_code=404, detail={"error": "没有新文件"})

    return FileResponse(
        path=str(tar_path),
        filename="generated-files.tar.gz",
        media_type="application/gzip",
        background=BackgroundTask(_cleanup_file, tar_path),
    )
