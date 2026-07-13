"""
=============================================================================
  AI Chat 后端主入口
  技术栈: Python 3.12 + FastAPI + aiomysql + JWT + bcrypt
  
  架构层次：
  main.py         → 启动入口，组装所有路由和中间件
  ├── config.py   → 集中配置管理
  ├── database.py → 异步 MySQL 连接池
  ├── auth.py     → JWT 认证 + 频率限制
  ├── models.py   → Pydantic 数据模型
  ├── routes_auth.py      → 登录/注册/忘记密码
  ├── routes_projects.py  → 项目管理
  ├── routes_files.py     → 文件下载
  ├── routes_stats.py     → 统计排名
  └── skills/     → 技能插件系统（可扩展）
  
  运行方式:
    python main.py
    或: uvicorn python_app.main:app --host 0.0.0.0 --port 3001
=============================================================================
"""
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# 将父目录加入路径，方便外部 uvicorn 直接运行
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent.parent))

from .config import JWT_SECRET, DB_CONFIG
from .database import init_db, close_db
from .auth import rate_limit_middleware


# ---------- 应用生命周期 ----------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理。
    
    startup:  初始化数据库连接池 → 加载技能插件
    shutdown: 关闭数据库连接池 → 清理资源
    """
    # === 启动 ===
    print("[启动] 连接数据库...")
    await init_db()
    print("[启动] 数据库连接就绪")

    # 加载技能插件
    from .skills import registry
    from .skills.hello import HelloSkill
    registry.register(HelloSkill())
    print("[启动] 安装技能插件...")
    await registry.install(app)

    yield  # 应用运行中

    # === 关闭 ===
    print("[关闭] 断开数据库连接...")
    await close_db()


# ---------- FastAPI 应用创建 ----------

app = FastAPI(
    title="AI Chat API",
    description="AI Chat Web 后端服务，提供用户认证、项目管理、文件下载和统计排名",
    version="2.0.0",
    lifespan=lifespan,
)

# 频率限制中间件（按路径+IP 限流）
app.middleware("http")(rate_limit_middleware)


# ---------- 全局错误处理器 ----------
# 目的：把 FastAPI 默认的 {"detail":...} 格式统一为前端期望的扁平格式

from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Pydantic 校验失败 -> 扁平返回"""
    msg = "请求参数错误"
    for err in exc.errors():
        ctx = err.get("ctx", {})
        if isinstance(ctx, dict) and "error" in ctx:
            err_obj = ctx["error"]
            if hasattr(err_obj, "args") and err_obj.args:
                msg = str(err_obj.args[0])
                break
        elif "msg" in err:
            raw = str(err["msg"])
            if raw.startswith("Value error, "):
                msg = raw[13:]
            else:
                msg = raw
            break
    return JSONResponse(
        status_code=400,
        content={"success": False, "message": msg},
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """服务器内部错误 -> 统一返回"""
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": "服务器内部错误"},
    )


from starlette.exceptions import HTTPException as StarletteHTTPException

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """HTTPException -> 扁平返回，前端可直接读取 error/message 字段"""
    detail = exc.detail
    if isinstance(detail, dict):
        return JSONResponse(status_code=exc.status_code, content=detail)
    return JSONResponse(status_code=exc.status_code, content={"error": str(detail)})


# ---------- 注册路由 ----------

from .routes_auth import router as auth_router
from .routes_projects import router as projects_router
from .routes_files import router as files_router
from .routes_stats import router as stats_router

app.include_router(auth_router)
app.include_router(projects_router)
app.include_router(files_router)
app.include_router(stats_router)


# ---------- 运行入口 ----------

if __name__ == "__main__":
    import uvicorn
    # 启动前检查关键配置
    if not JWT_SECRET:
        print("[错误] 请设置 JWT_SECRET 环境变量")
        sys.exit(1)
    if not DB_CONFIG.get("password"):
        print("[错误] 请设置 DB_PASSWORD 环境变量")
        sys.exit(1)

    print("[启动] 服务监听: http://0.0.0.0:3001")
    print("[文档] API 文档: http://0.0.0.0:3001/docs")
    uvicorn.run(app, host="0.0.0.0", port=3001)
