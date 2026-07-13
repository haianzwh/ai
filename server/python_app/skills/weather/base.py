"""
查询天气预报
"""
from fastapi import FastAPI, APIRouter

NAME = "weather"
DESC = "查询天气预报"


class WeatherSkill:
    name = NAME
    description = DESC

    async def on_register(self, app: FastAPI):
        router = APIRouter(prefix="/api/skills/weather", tags=["weather"])

        @router.get("")
        async def info():
            return {
                "skill": "weather",
                "description": "查询天气预报",
            }

        @router.get("/run")
        async def run():
            return {"status": "ok", "message": "weather running"}

        app.include_router(router)
