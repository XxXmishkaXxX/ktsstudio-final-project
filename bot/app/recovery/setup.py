import asyncio
import typing
if typing.TYPE_CHECKING:
    from app.web.app import Application
from app.recovery.recovery import RecoveryService
from app.recovery.heartbeat import HeartbeatService

def setup_recovery(app: "Application"):
    app.heartbeat = HeartbeatService(app)
    app.recovery = RecoveryService(app)

    async def on_startup(app: "Application"):
        asyncio.create_task(app.recovery.recover_all_games())

    app.on_startup.append(on_startup)
