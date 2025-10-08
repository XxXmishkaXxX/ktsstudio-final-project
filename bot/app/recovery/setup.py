import asyncio
import typing

if typing.TYPE_CHECKING:
    from app.web.app import Application
from app.recovery.heartbeat import HeartbeatService
from app.recovery.recovery import RecoveryService


def setup_recovery(app: "Application"):
    app.heartbeat = HeartbeatService(app)
    app.recovery = RecoveryService(app)

    app.on_startup.append(asyncio.create_task(app.recovery.recover_all_games()))
