"""
=============================================================================
  项目路由
  项目列表 / 创建项目 / 项目文件列表
=============================================================================
"""
import httpx
from fastapi import APIRouter, HTTPException, Depends

from .database import execute, execute_write
from .auth import get_current_user
from .config import OPENCODE_BASE_URL, MAX_FILES, FILE_DIR, SEARCH_DIRS, NEWER_REF, FIND_EXCLUDES
from .models import (
    ProjectItem, ProjectListResponse, ProjectCreateResponse,
    FileItem, FileListResponse,
)

router = APIRouter(prefix="/api", tags=["项目"])


@router.get("/projects", response_model=ProjectListResponse)
async def list_projects(user: dict = Depends(get_current_user)):
    """
    获取当前登录用户的项目列表。
    流程：获取 opencode sessions -> 过滤出属于当前用户的 -> 返回
    """
    current_user = user["username"]

    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{OPENCODE_BASE_URL}/api/session")
        sessions = resp.json().get("data", [])

    rows = await execute(
        "SELECT session_id FROM user_sessions WHERE username = %s",
        (current_user,),
    )
    user_session_ids = {r["session_id"] for r in rows}

    projects = []
    for s in sessions:
        if s["id"] in user_session_ids:
            projects.append(ProjectItem(
                id=s["id"],
                title=s.get("title") or "未命名",
                dir=s.get("location", {}).get("directory", "/home"),
                updated=str(s.get("time", {}).get("updated", "")),
                tokens=(s.get("tokens", {}).get("input", 0) or 0) +
                       (s.get("tokens", {}).get("output", 0) or 0),
            ))

    return ProjectListResponse(projects=projects, username=current_user)


@router.post("/projects", response_model=ProjectCreateResponse)
async def create_project(user: dict = Depends(get_current_user)):
    """
    创建新项目（opencode 会话）。
    调用 opencode API 新建 session -> 绑定到当前用户 -> 返回
    """
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{OPENCODE_BASE_URL}/api/session",
            json={},
        )
        data = resp.json()
        session = data.get("data", {})

    session_id = session.get("id")
    if not session_id:
        raise HTTPException(status_code=500, detail={"success": False, "message": "创建失败"})

    await execute_write(
        "INSERT IGNORE INTO user_sessions (username, session_id, tokens_input, tokens_output, tokens_reasoning) VALUES (%s, %s, 0, 0, 0)",
        (user["username"], session_id),
    )

    return ProjectCreateResponse(
        id=session_id,
        title=session.get("title", "新项目"),
    )


@router.get("/projects/{project_id}/files")
async def list_project_files(
    project_id: str, user: dict = Depends(get_current_user)
) -> dict:
    """
    获取项目文件列表。
    流程：
    1. find 搜索生成文件（排除源代码）
    2. 复制到项目专属目录
    3. 清理旧文件（保留最新100个）
    """
    import subprocess
    import shutil
    from pathlib import Path

    seen: set[str] = set()
    files: list[dict] = []

    # 构建 find 排除参数
    exclude_args: list[str] = []
    for ex in FIND_EXCLUDES:
        if ex.startswith("-"):
            exclude_args.extend(["-not", "-name", ex.lstrip("-")])
        elif "*" in ex:
            exclude_args.extend(["-not", "-path", ex])
        else:
            exclude_args.extend(["-not", "-path", ex])

    for search_dir in SEARCH_DIRS:
        try:
            cmd = ["find", search_dir, "-maxdepth", "3", "-type", "f", "-newer", NEWER_REF] + exclude_args
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            for fp in result.stdout.strip().split("\n"):
                fp = fp.strip()
                if not fp or fp in seen:
                    continue
                if fp.endswith(".log") or fp.endswith(".lock"):
                    continue
                fpath = Path(fp)
                try:
                    stat = fpath.stat()
                except OSError:
                    continue
                if stat.st_size < 50:
                    continue
                seen.add(fp)
                files.append({
                    "name": fpath.name, "path": fp,
                    "size": stat.st_size, "mtime": stat.st_mtime.strftime("%Y-%m-%dT%H:%M:%S"),
                })
        except (subprocess.TimeoutExpired, Exception):
            pass

    # 按时间降序
    files.sort(key=lambda f: f["mtime"], reverse=True)

    # 复制到项目专属目录
    short_id = project_id[:8]
    project_dir = FILE_DIR / short_id
    project_dir.mkdir(parents=True, exist_ok=True)

    for f in files[:MAX_FILES]:
        dest = project_dir / f["name"]
        if not dest.exists():
            try:
                shutil.copy2(f["path"], str(dest))
            except OSError:
                pass

    # 清理旧文件
    _clean_dir(project_dir)

    return {"success": True, "files": files[:MAX_FILES]}


def _clean_dir(directory) -> None:
    """清理目录，只保留最新 MAX_FILES 个文件，安全：仅清理 generated_files"""
    from pathlib import Path
    d = Path(directory) if not isinstance(directory, Path) else directory
    if "generated_files" not in str(d):
        return
    try:
        sorted_files = sorted(
            [f for f in d.iterdir() if f.is_file()],
            key=lambda f: f.stat().st_mtime,
            reverse=True,
        )
        for f in sorted_files[MAX_FILES:]:
            f.unlink()
    except Exception:
        pass
