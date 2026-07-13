"""
=============================================================================
  认证路由
  登录 / 注册 / 忘记密码
=============================================================================
"""
import bcrypt
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse

from .database import execute, execute_one, execute_write
from .auth import create_token, get_current_user
from .models import (
    LoginRequest, RegisterRequest, ForgotPasswordRequest,
    LoginResponse, UserInfo, ErrorResponse,
)

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/login", response_model=LoginResponse, responses={401: {"model": ErrorResponse}})
async def login(req: LoginRequest, request: Request):
    """
    用户登录。
    
    流程：
    1. 查数据库校验用户名密码 -> bcrypt 比对哈希
    2. 签发 48 小时 JWT 令牌
    3. 更新最后登录时间
    4. 返回 token 和用户信息（不含密码）
    
    安全: 频率限制由中间件控制，同一 IP 每分钟最多 10 次
    """
    user = await execute_one(
        "SELECT * FROM users WHERE username = %s AND status = %s",
        (req.username, "active"),
    )
    if not user:
        raise HTTPException(status_code=401, detail={"success": False, "message": "用户名或密码错误"})

    # bcrypt 比对: 用户输入的密码 vs 数据库中的哈希值
    if not bcrypt.checkpw(req.password.encode(), user["password"].encode()):
        raise HTTPException(status_code=401, detail={"success": False, "message": "用户名或密码错误"})

    # 签发 token（载荷: 用户ID + 用户名）
    token = create_token(user["id"], user["username"])

    # 更新登录时间
    await execute_write("UPDATE users SET last_login = NOW() WHERE id = %s", (user["id"],))

    return LoginResponse(
        success=True,
        token=token,
        user=UserInfo(id=user["id"], username=user["username"], email=user["email"]),
    )


@router.post("/register", responses={400: {"model": ErrorResponse}, 409: {"model": ErrorResponse}})
async def register(req: RegisterRequest):
    """
    用户注册。
    
    校验规则（Pydantic 自动执行）:
    - 用户名: 3-20位，字母数字下划线
    - 密码: 至少8位，必须包含字母和数字
    - 邮箱: 标准格式
    
    安全: 密码 bcrypt 哈希存储，不使用明文
    """
    # 查重：用户名是否已存在
    existing = await execute_one("SELECT id FROM users WHERE username = %s", (req.username,))
    if existing:
        raise HTTPException(status_code=409, detail={"success": False, "message": "用户名已存在"})

    # 密码加盐哈希 (cost factor=10)
    hashed = bcrypt.hashpw(req.password.encode(), bcrypt.gensalt(rounds=10))

    await execute_write(
        "INSERT INTO users (username, password, email) VALUES (%s, %s, %s)",
        (req.username, hashed.decode(), req.email),
    )

    return {"success": True}


@router.post("/forgot-password", responses={404: {"model": ErrorResponse}})
async def forgot_password(req: ForgotPasswordRequest):
    """
    忘记密码。
    
    校验用户名和邮箱是否匹配 -> 提示联系管理员重置。
    当前未实现自动发邮件功能，预留扩展接口。
    """
    user = await execute_one(
        "SELECT id FROM users WHERE username = %s AND email = %s",
        (req.username, req.email),
    )
    if not user:
        raise HTTPException(status_code=404, detail={"success": False, "message": "用户名或邮箱不匹配"})

    return JSONResponse(content={"success": True, "message": "请联系管理员重置密码"})


@router.get("/me")
async def get_me(user: dict = __import__("fastapi").Depends(get_current_user)):
    """
    获取当前登录用户信息。
    用途: 前端检查登录状态，获取当前用户名。
    """
    u = await execute_one(
        "SELECT id, username, email FROM users WHERE id = %s",
        (user["id"],),
    )
    if not u:
        raise HTTPException(status_code=404, detail={"error": "用户不存在"})
    return {"success": True, "user": UserInfo(id=u["id"], username=u["username"], email=u["email"])}
