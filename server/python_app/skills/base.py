"""
=============================================================================
  技能插件系统基类
  定义技能的抽象接口，供具体技能实现继承。
  
  后期扩展方式：
  1. 在 skills/ 目录下新建 Python 文件（如 ppt_skill.py）
  2. 继承 BaseSkill 并实现 on_register() 方法
  3. 在 skills/registry.py 中注册
=============================================================================
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any
from fastapi import FastAPI


class BaseSkill(ABC):
    """
    技能基类。
    
    每个技能实现以下接口：
    - name: 技能名称（用于日志和注册表）
    - description: 技能描述
    - on_register(app): 插件注册回调，在此钩子中注册路由/事件/中间件
    """

    name: str = "unnamed_skill"
    description: str = ""

    @abstractmethod
    async def on_register(self, app: FastAPI) -> None:
        """
        技能注册回调。
        
        当技能被加载时调用，传入 FastAPI app 实例。
        在此方法中可：
        - 注册新的 API 路由: app.include_router(router)
        - 注册事件处理器: app.add_event_handler("startup", handler)
        - 添加中间件: app.middleware("http")(handler)
        
        示例：
            router = APIRouter(prefix="/api/skills/my_skill")
            
            @router.get("/do")
            async def do_something():
                return {"result": "done"}
            
            app.include_router(router)
        """
        ...
