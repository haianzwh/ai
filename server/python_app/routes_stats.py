"""
=============================================================================
  统计排名路由
  项目 Token 排名 / 用户 Token 排名
=============================================================================
"""
from datetime import datetime, timezone, timedelta
import httpx
from fastapi import APIRouter, Depends, Query

from .database import execute, execute_write
from .auth import get_current_user
from .config import OPENCODE_BASE_URL, ONLINE_THRESHOLD_MS, ADMIN_USERNAME

router = APIRouter(prefix="/api/stats", tags=["统计"])


def _mask(s: str) -> str:
    """隐私遮蔽：只显示首尾字符，中间用*代替"""
    if not s:
        return ""
    if len(s) <= 2:
        return s[0] + "*"
    hidden_len = min(len(s) - 2, 4)
    return s[0] + "*" * hidden_len + s[-1]


@router.get("/ranking")
async def project_ranking(
    user: dict = Depends(get_current_user),
    type: str = Query("daily", description="daily=今日, all=累计"),
):
    """
    项目 Token 排名（默认按今日消耗排序）。

    从 opencode 获取所有会话，按标题聚合 Token 用量，
    按 total 降序排列返回前 50 名。
    
    参数 type=daily → 仅统计今日会话（默认）
    参数 type=all   → 统计全部历史会话
    """
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{OPENCODE_BASE_URL}/api/session")
        sessions = resp.json().get("data", [])

    # 如果是 daily 模式，过滤出今日有活动的 session
    if type == "daily":
        today_ms_start = int(datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        ).timestamp() * 1000)
        sessions = [
            s for s in sessions
            if (s.get("time", {}).get("updated", 0) or 0) >= today_ms_start
        ]

    # 按标题聚合
    stats: dict[str, dict] = {}
    for s in sessions:
        key = s.get("title") or "未命名"
        if key not in stats:
            stats[key] = {
                "name": key, "input": 0, "output": 0,
                "reasoning": 0, "sessions": 0,
                "dir": s.get("location", {}).get("directory", ""),
            }
        tokens = s.get("tokens", {})
        stats[key]["input"] += tokens.get("input", 0) or 0
        stats[key]["output"] += tokens.get("output", 0) or 0
        stats[key]["reasoning"] += tokens.get("reasoning", 0) or 0
        stats[key]["sessions"] += 1

    # 计算 total + 排序
    ranking = []
    for item in stats.values():
        item["total"] = item["input"] + item["output"] + item["reasoning"]
        ranking.append(item)
    ranking.sort(key=lambda x: x["total"], reverse=True)

    # 汇总
    totals = {"input": 0, "output": 0, "reasoning": 0, "total": 0, "sessions": 0}
    for item in ranking:
        totals["input"] += item["input"]
        totals["output"] += item["output"]
        totals["reasoning"] += item["reasoning"]
        totals["total"] += item["total"]
        totals["sessions"] += item["sessions"]

    return {"success": True, "ranking": ranking[:50], "totals": totals}


@router.get("/users")
async def user_ranking(user: dict = Depends(get_current_user)):
    """
    用户 Token 排名。
    
    流程：
    1. 获取 opencode sessions，将未记录的归给当前用户
    2. 更新用户 Token 累计和活跃时间
    3. 查询所有用户排名，隐私遮蔽非管理员信息
    """
    current_user = user
    is_admin = current_user["username"] == ADMIN_USERNAME

    # 获取 sessions
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{OPENCODE_BASE_URL}/api/session")
        sessions = resp.json().get("data", [])

    # 获取已记录 session（去重）
    recorded_rows = await execute("SELECT session_id FROM user_sessions")
    recorded_ids = {r["session_id"] for r in recorded_rows}

    # 归属未记录 session 给当前用户
    new_tokens = 0
    for s in sessions:
        if s["id"] not in recorded_ids:
            tokens = s.get("tokens", {})
            inp = tokens.get("input", 0) or 0
            out = tokens.get("output", 0) or 0
            reason = tokens.get("reasoning", 0) or 0
            total = inp + out + reason
            if total > 0:
                await execute_write(
                    "INSERT IGNORE INTO user_sessions (username, session_id, tokens_input, tokens_output, tokens_reasoning) VALUES (%s, %s, %s, %s, %s)",
                    (current_user["username"], s["id"], inp, out, reason),
                )
                new_tokens += total

    # 更新用户 Token 和活跃时间
    if new_tokens > 0:
        await execute_write(
            "UPDATE users SET total_tokens = COALESCE(total_tokens,0) + %s, last_active = NOW() WHERE username = %s",
            (new_tokens, current_user["username"]),
        )
    else:
        await execute_write(
            "UPDATE users SET last_active = NOW() WHERE username = %s",
            (current_user["username"],),
        )

    # 总 Token
    total_tokens = sum(
        (s.get("tokens", {}).get("input", 0) or 0) +
        (s.get("tokens", {}).get("output", 0) or 0) +
        (s.get("tokens", {}).get("reasoning", 0) or 0)
        for s in sessions
    )

    # 查询所有活跃用户
    user_rows = await execute(
        "SELECT id, username, email, created_at, last_login, last_active, COALESCE(total_tokens,0) AS total_tokens FROM users WHERE status = %s ORDER BY COALESCE(total_tokens,0) DESC",
        ("active",),
    )

    now = datetime.now(timezone.utc)
    users_list = []
    for u in user_rows:
        is_me = u["id"] == current_user["id"]
        is_online = False
        if u["last_active"]:
            diff_ms = (now - u["last_active"].replace(tzinfo=timezone.utc)).total_seconds() * 1000
            is_online = diff_ms < ONLINE_THRESHOLD_MS

        users_list.append({
            "id": u["id"],
            "username": u["username"] if (is_admin or is_me) else _mask(u["username"]),
            "email": u["email"] if (is_admin or is_me) else _mask(u["email"]),
            "totalTokens": u["total_tokens"],
            "isMe": is_me,
            "isOnline": is_online,
            "lastLogin": u["last_login"].strftime("%Y-%m-%d %H:%M") if u["last_login"] else "从未登录",
        })

    return {
        "success": True,
        "users": users_list,
        "totalSessions": len(sessions),
        "totalTokens": total_tokens,
        "currentUser": current_user["username"],
    }
