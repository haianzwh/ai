from ..base import Skill


class SendEmailSkill(Skill):
    name = "send_email"
    description = "Send an email"

    @property
    def parameters(self):
        return {"type": "object", "properties": {"to": {"type": "string"}, "subject": {"type": "string"}, "body": {"type": "string"}}, "required": ["to", "subject", "body"]}

    async def execute(self, to: str = "", subject: str = "", body: str = "", **kwargs):
        return {"status": "sent", "to": to, "subject": subject}
