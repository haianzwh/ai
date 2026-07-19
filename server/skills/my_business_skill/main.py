from python_app.acp.skills.base import Skill


class MyBusinessSkill(Skill):
    name = "my_business_skill"
    description = "Handle business logic"

    async def execute(self, **kwargs):
        return {"message": "Business skill executed"}


skill = MyBusinessSkill()
