"""
=============================================================================
  文件上传 & 下载路由
  单文件上传 / 文件列表 / 单文件下载 / 项目打包 / 一键下载
=============================================================================
"""
import subprocess
import shutil
import aiofiles
import os
from pathlib import Path
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from starlette.background import BackgroundTask

from .auth import get_current_user
from .config import ALLOWED_DIRS, FILE_DIR, OPENCODE_BASE_URL, MAX_FILES

# 用户上传文件存放目录
UPLOAD_DIR = FILE_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

router = APIRouter(prefix="/api", tags=["文件"])


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


# ========== 文件上传 ==========

@router.post("/upload")
async def upload_file(
    file: UploadFile,
    user: dict = Depends(get_current_user),
):
    """
    上传文件到服务器。
    
    支持任意文件类型，保存到 generated_files/uploads/ 目录。
    文件名自动加时间戳前缀，防止重名覆盖。
    """
    # 生成带时间戳+用户名的文件名（避免重名冲突）
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = f"{user['username']}_{timestamp}_{file.filename}"

    dest = UPLOAD_DIR / safe_name

    # 异步写入文件
    async with aiofiles.open(str(dest), "wb") as f:
        content = await file.read()
        await f.write(content)

    return JSONResponse(content={
        "success": True,
        "filename": safe_name,
        "original": file.filename,
        "size": len(content),
        "path": str(dest),
    })


@router.get("/uploads")
async def list_uploads(user: dict = Depends(get_current_user)):
    """
    列出所有上传的文件（按时间倒序）。
    """
    files = []
    if UPLOAD_DIR.exists():
        for f in sorted(
            UPLOAD_DIR.iterdir(),
            key=lambda x: x.stat().st_mtime,
            reverse=True,
        ):
            if f.is_file():
                # 文件名格式: 用户名_YYYYMMDD_HHMMSS_原始名 → 提取原始名
                name = f.name
                parts = name.split("_")
                # 格式: 至少 username(1) + date(2) + time(3) + original(4+)
                # 旧格式: date(1) + time(2) + original(3+)
                if len(parts) >= 4 and not parts[0].isdigit():
                    orig = "_".join(parts[3:])  # 用户名开头的格式
                elif len(parts) >= 3 and parts[0].isdigit():
                    orig = "_".join(parts[2:])  # 旧日期开头的格式
                else:
                    orig = name
                files.append({
                    "name": name,
                    "orig": orig,
                    "size": f.stat().st_size,
                    "time": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
                    "path": str(f),
                })

    return {"success": True, "files": files}
