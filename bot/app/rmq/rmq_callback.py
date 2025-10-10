import json
import typing

import aio_pika

from app.bot.handlers.callback import handle_callback
from app.bot.handlers.command import handle_command

if typing.TYPE_CHECKING:
    from app.web.app import Application


async def rmq_callback(message: aio_pika.IncomingMessage, app: "Application"):
    async with message.process():
        try:
            payload = json.loads(message.body.decode())

            if "callback_query" in payload:
                chat_id = payload["callback_query"]["message"]["chat"]["id"]

                data = json.loads(payload["callback_query"]["data"])
                callback_type = data["t"]
                game_id = data["g"]
                round_id = data.get("r")
                team = data.get("team")

                message_id = payload["callback_query"]["message"]["message_id"]
                callback_id = payload["callback_query"]["id"]
                user_data = payload["callback_query"]["from"]

                await handle_callback(
                    app,
                    callback_type,
                    game_id,
                    chat_id,
                    callback_id,
                    message_id,
                    user_data,
                    team=team,
                    round_id=round_id,
                )
            elif "message" in payload:
                msg = payload["message"]
                chat_id = msg["chat"]["id"]
                text = msg.get("text", "")
                user_data = msg.get("from", {})
                chat_type = msg["chat"]["type"]

                command = None
                args = ""

                for e in msg.get("entities", []):
                    if e["type"] == "bot_command":
                        command = text[e["offset"] : e["offset"] + e["length"]]
                        args = text[e["offset"] + e["length"] :].strip()
                        break

                if command:
                    await handle_command(
                        app, command, chat_id, user_data, chat_type, args=args
                    )

        except Exception as e:
            app.logger.error("⚠️ Failed to handle message: %s", e)
