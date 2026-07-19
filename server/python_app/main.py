"""
=============================================================================
  AI Chat 后端主入口 — ACP 全架构
=============================================================================
"""
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent))

from .config import JWT_SECRET, DB_CONFIG
from .database import init_db, close_db
from .auth import rate_limit_middleware

BASE = Path(__file__).parent


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ============================
    # 数据库
    # ============================
    print("[启动] 连接数据库...")
    await init_db()
    print("[启动] 数据库连接就绪")

    # ============================
    # 技能插件（legacy）
    # ============================
    from .skills import registry as legacy_skill_registry
    from .skills.hello import HelloSkill
    from .skills.photo_edit import PhotoEditSkill
    from .skills.skill_creator import SkillCreator as SkillCreatorSkill
    legacy_skill_registry.register(HelloSkill())
    legacy_skill_registry.register(PhotoEditSkill())
    legacy_skill_registry.register(SkillCreatorSkill())
    print("[启动] 安装技能插件...")
    await legacy_skill_registry.install(app)

    # ============================
    # Provider 加载
    # ============================
    print("[启动] 加载 AI Provider...")
    from .agent.registry import registry as provider_registry
    from .agent.opencode import OpenCodeProvider
    provider_registry.register(OpenCodeProvider)
    provider_cfg_path = BASE / "config" / "providers.yaml"
    if provider_cfg_path.exists():
        provider_registry.load_config(provider_cfg_path)
    print("[启动] AI Provider 就绪")

    # ============================
    # ACP Skill 系统（新）
    # ============================
    from .acp.skills import (
        skill_registry, load_skills_from_dir,
        WebSearchSkill, CalculatorSkill, CodeExecutorSkill,
        FileReaderSkill, SendEmailSkill,
    )
    skill_registry.register(WebSearchSkill())
    skill_registry.register(CalculatorSkill())
    skill_registry.register(CodeExecutorSkill())
    skill_registry.register(FileReaderSkill())
    skill_registry.register(SendEmailSkill())
    from .acp.skills.builtin.doc_analyzer import DocumentAnalysisSkill
    skill_registry.register(DocumentAnalysisSkill())
    from .acp.skills.builtin.skill_generator import SkillGeneratorSkill
    skill_registry.register(SkillGeneratorSkill())
    load_skills_from_dir(str(BASE.parent / "skills"))
    print(f"[启动] ACP Skills: {skill_registry.list_all()}")

    # ============================
    # 中间件插件
    # ============================
    from .acp.middleware import (
        plugin_registry,
        LoggingMiddleware, RateLimitMiddleware,
        PromptInjectorPlugin, ResponseFormatterPlugin,
    )
    plugin_registry.register(LoggingMiddleware())
    plugin_registry.register(RateLimitMiddleware())
    plugin_registry.register(ResponseFormatterPlugin())
    await plugin_registry.setup_all()
    print(f"[启动] 插件: {[p['name'] for p in plugin_registry.list()]}")

    # ============================
    # Memory
    # ============================
    from .acp.memory import MemoryManager
    memory_mgr = MemoryManager()
    app.state.memory = memory_mgr
    print("[启动] Memory 就绪")

    # ============================
    # RAG
    # ============================
    from .acp.rag import SimpleRAG, Retriever
    rag = SimpleRAG()
    retriever = Retriever(rag)
    app.state.rag = rag
    app.state.retriever = retriever
    print("[启动] RAG 就绪")

    # ============================
    # Cache
    # ============================
    from .acp.cache import PromptCache, EmbeddingCache, ResultCache
    app.state.prompt_cache = PromptCache()
    app.state.embedding_cache = EmbeddingCache()
    app.state.result_cache = ResultCache()
    print("[启动] Cache 就绪")

    # ============================
    # Event
    # ============================
    from .acp.events import ACPEvent, EventEmitter
    from .acp.events.handlers import logging_handler, audit_handler
    emitter = EventEmitter()
    emitter.on("chat.completions", logging_handler)
    emitter.on("chat.completions", audit_handler)
    app.state.event_emitter = emitter
    print("[启动] Event 就绪")

    # ============================
    # Eval
    # ============================
    from .acp.eval import EvalRunner
    eval_runner = EvalRunner()
    app.state.eval_runner = eval_runner
    print("[启动] Eval 就绪")

    # ============================
    # ACP 引擎
    # ============================
    print("[启动] 初始化 ACP 引擎...")
    from .acp.server import ACPServer
    from .acp.client import ACPClient
    from .acp.external.gateway import ExternalACPGateway
    from .acp.workflow import WorkflowEngine

    with open(provider_cfg_path) as f:
        provider_config = yaml.safe_load(f) or {}

    external_gateway = ExternalACPGateway()
    app.state.acp_gateway = external_gateway

    acp_server = ACPServer(external_gateway=external_gateway)
    acp_server.register_provider_routes(provider_config.get("providers", {}))
    app.state.acp_server = acp_server

    acp_client = ACPClient(server=acp_server)
    app.state.acp_client = acp_client

    from .process.chat import set_acp_client, set_memory_manager
    set_acp_client(acp_client)
    set_memory_manager(memory_mgr)

    wf_engine = WorkflowEngine(skill_registry=skill_registry, plugin_registry=plugin_registry)
    wf_engine.load_dir(str(BASE / "acp" / "workflow" / "workflows"))
    wf_engine.load_dir(str(BASE.parent / "workflows"))
    app.state.workflow_engine = wf_engine

    from .acp.handlers.workflow import set_workflow_engine
    set_workflow_engine(wf_engine)

    await external_gateway.initialize(provider_config.get("providers", {}))
    print("[启动] ACP 引擎就绪")

    # 注入各层依赖
    from .routes.chat import set_acp_server as _s1
    from .routes.workflows import set_workflow_engine as _s2
    from .routes.admin import set_memory_manager as _s3
    _s1(acp_server)
    _s2(wf_engine)
    _s3(memory_mgr)

    yield

    # ============================
    # Shutdown
    # ============================
    print("[关闭] 关闭外部 Agent...")
    await external_gateway.shutdown()
    await plugin_registry.teardown_all()
    print("[关闭] 断开数据库连接...")
    await close_db()


# ============================
# FastAPI 应用
# ============================
app = FastAPI(title="AI Chat API — ACP", version="2.1.0", lifespan=lifespan)
app.middleware("http")(rate_limit_middleware)

# 全局错误处理
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    msg = "请求参数错误"
    for err in exc.errors():
        ctx = err.get("ctx", {})
        if isinstance(ctx, dict) and "error" in ctx:
            err_obj = ctx["error"]
            if hasattr(err_obj, "args") and err_obj.args:
                msg = str(err_obj.args[0]); break
        elif "msg" in err:
            raw = str(err["msg"])
            msg = raw[13:] if raw.startswith("Value error, ") else raw; break
    return JSONResponse(status_code=400, content={"success": False, "message": msg})

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    return JSONResponse(status_code=500, content={"success": False, "message": "服务器内部错误"})

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    detail = exc.detail
    if isinstance(detail, dict):
        return JSONResponse(status_code=exc.status_code, content=detail)
    return JSONResponse(status_code=exc.status_code, content={"error": str(detail)})


# ============================
# 注册路由
# ============================
from .routes_auth import router as auth_router
from .routes_projects import router as projects_router
from .routes_files import router as files_router
from .routes_stats import router as stats_router
from .routes.chat import router as chat_router, set_acp_server as _set_chat_acp
from .routes.skills import router as skills_router
from .routes.workflows import router as workflows_router, set_workflow_engine as _set_wf
from .routes.admin import router as admin_router

app.include_router(auth_router)
app.include_router(projects_router)
app.include_router(files_router)
app.include_router(stats_router)
app.include_router(chat_router)
app.include_router(skills_router)
app.include_router(workflows_router)
app.include_router(admin_router)

# 静态文件（前端）
pub = BASE.parent / "public"
if pub.exists():
    app.mount("/", StaticFiles(directory=str(pub), html=True), name="public")


# ============================
# 运行入口
# ============================
if __name__ == "__main__":
    import uvicorn
    if not JWT_SECRET:
        print("[错误] 请设置 JWT_SECRET 环境变量"); sys.exit(1)
    if not DB_CONFIG.get("password"):
        print("[错误] 请设置 DB_PASSWORD 环境变量"); sys.exit(1)
    print("[启动] 服务监听: http://0.0.0.0:3001")
    uvicorn.run(app, host="0.0.0.0", port=3001)
