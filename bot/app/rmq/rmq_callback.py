import json
import typing

import aio_pika
from app.bot.handlers.command import handle_command

if typing.TYPE_CHECKING:
    from app.web.app import Application


async def rmq_callback(message: aio_pika.IncomingMessage, app: "Application"):
    async with message.process():
        try:
            payload = json.loads(message.body.decode())

            if "message" in payload:
                msg = payload["message"]
                chat_id = msg["chat"]["id"]
                text = msg.get("text", "")
                user_data = msg.get("from", {})
                chat_type = msg["chat"]["type"]
                command = next(
                    (
                        text[e["offset"] : e["offset"] + e["length"]]
                        for e in msg.get("entities", [])
                        if e["type"] == "bot_command"
                    ),
                    None,
                )

                if command:
                    await handle_command(
                        app, command, chat_id, user_data, chat_type
                    )
            app.logger.info(json.dumps(payload))

        except Exception as e:
            app.logger.error("⚠️ Failed to handle message: %s", e)
