import json
import typing

import aio_pika

if typing.TYPE_CHECKING:
    from app.web.app import Application


async def rmq_callback(message: aio_pika.IncomingMessage, app: "Application"):
    async with message.process():
        try:
            payload = json.loads(message.body.decode())
            app.logger.info(json.dumps(payload))
        except Exception as e:
            app.logger.error("⚠️ Failed to handle message: %s", e)
