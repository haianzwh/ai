from python_app.acp.middleware.base import Plugin


class BusinessPlugin(Plugin):
    name = "business_plugin"
    priority = 60

    async def on_response(self, method, params, result):
        if isinstance(result, dict):
            result["_plugin"] = "business"
        return result


plugin = BusinessPlugin()
