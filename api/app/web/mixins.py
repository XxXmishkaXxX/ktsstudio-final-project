import json
from aiohttp import web
from aiohttp_session import get_session


class AdminRequiredMixin:
    async def _iter(self) -> web.StreamResponse:
        await self.prepare()
        return await super()._iter()

    async def prepare(self):
        session = await get_session(self.request)
        if not session or session.get("role") != "admin":
            raise web.HTTPUnauthorized(
                text=json.dumps({"status": "unauthorized"}),
                content_type="application/json"
            )
        self.request.admin = {
            "id": session.get("id"),
            "email": session.get("email")
        }
        self.request.session = session
