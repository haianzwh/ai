"""
=============================================================================
  认证与安全模块
  JWT 令牌签发/验证 + 频率限制 + 认证中间件
=============================================================================
"""
import time
import jwt
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from .config import JWT_SECRET, JWT_EXPIRE_HOURS, RATE_LIMITS


# ---------- JWT 令牌工具 ----------

def create_token(user_id: int, username: str) -> str:
    """
    签发 JWT 令牌。
    载荷中存入用户ID和用户名，后端路由可从中提取用户身份。
    """
    payload = {
        "id": user_id,
        "username": username,
        "iat": int(time.time()),                      # 签发时间
        "exp": int(time.time()) + JWT_EXPIRE_HOURS * 3600,  # 过期时间
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def verify_token(token: str) -> dict:
    """
    验证 JWT 令牌，返回解码后的载荷（包含 id, username）。
    令牌无效或过期时抛出异常。
    """
    return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])


# ---------- 内存频率限制 ----------

# 存储结构: { "login:192.168.1.1": [timestamp1, timestamp2, ...], ... }
_rate_store: dict[str, list[float]] = {}


def rate_limit(key: str, max_req: int = 10, window_secs: float = 60.0) -> bool:
    """
    检查指定 key 是否超频。
    
    - key: 限制标识，如 "login:192.168.1.1"
    - max_req: 窗口内最大请求数
    - window_secs: 时间窗口（秒）
    
    Returns: True 表示未超限，False 表示超限需要等待。
    """
    now = time.time()
    if key not in _rate_store:
        _rate_store[key] = []
    # 清理窗口之外的旧记录
    _rate_store[key] = [t for t in _rate_store[key] if now - t < window_secs]
    if len(_rate_store[key]) >= max_req:
        return False  # 超限
    _rate_store[key].append(now)
    return True


# ---------- 速率限制中间件 ----------

async def rate_limit_middleware(request: Request, call_next):
    """
    FastAPI 中间件：在请求处理前检查频率限制。
    
    对特定路径（login/register/forgot）启用限制，
    超出限制时返回 429 而不是执行路由。
    """
    path = request.url.path
    # 只为认证相关接口开启频率限制
    limit_config = None
    if "/auth/login" in path and request.method == "POST":
        limit_config = RATE_LIMITS.get("login")
    elif "/auth/register" in path and request.method == "POST":
        limit_config = RATE_LIMITS.get("register")
    elif "/auth/forgot" in path and request.method == "POST":
        limit_config = RATE_LIMITS.get("forgot")

    if limit_config:
        max_req, window = limit_config
        ip = request.client.host if request.client else "unknown"
        key = f"{path}:{ip}"
        if not rate_limit(key, max_req, window):
            return JSONResponse(
                status_code=429,
                content={"success": False, "message": "请求过于频繁，请稍后再试"}
            )

    return await call_next(request)


# ---------- 认证依赖（FastAPI Depends）----------

async def get_current_user(request: Request) -> dict:
    """
    从请求中提取并验证用户身份。
    
    支持两种传 token 方式：
    1. Authorization: Bearer <token>  (优先)
    2. Cookie: auth_token=<token>
    
    验证通过返回字典 {"id": int, "username": str}
    验证失败抛出 401 HTTPException
    """
    # 方式一：从 Authorization Header 提取
    token: str | None = None
    auth_header = request.headers.get("authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]  # 去掉 "Bearer " 前缀

    # 方式二：从 Cookie 提取
    if not token:
        token = request.cookies.get("auth_token")

    if not token:
        raise HTTPException(status_code=401, detail={"error": "请先登录"})

    try:
        payload = verify_token(token)
        return {"id": payload["id"], "username": payload["username"]}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail={"error": "登录已过期"})
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail={"error": "无效的令牌"})
