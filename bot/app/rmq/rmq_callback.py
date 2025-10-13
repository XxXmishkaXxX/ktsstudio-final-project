import typing

import aio_pika

from app.bot.handlers.callback import handle_callback
from app.bot.handlers.command import handle_command
from app.rmq.utils import (
    extract_callback_data,
    extract_message_data,
    parse_json_body,
)

if typing.TYPE_CHECKING:
    from app.web.app import Application


async def rmq_callback(message: aio_pika.IncomingMessage, app: "Application"):
    """Главная точка обработки сообщений из RabbitMQ."""
    try:
        async with message.process():
            payload = parse_json_body(message)

            if "callback_query" in payload:
                data = extract_callback_data(payload)
                await handle_callback(
                    app,
                    data["callback_type"],
                    data["game_id"],
                    data["chat_id"],
                    data["callback_id"],
                    data["message_id"],
                    data["user_data"],
                    team=data["team"],
                    team_num=data["team_num"],
                    round_id=data["round_id"],
                )

            elif "message" in payload:
                msg_data = extract_message_data(payload)
                if msg_data["command"]:
                    await handle_command(
                        app,
                        msg_data["command"],
                        msg_data["chat_id"],
                        msg_data["user_data"],
                        msg_data["chat_type"],
                        args=msg_data["args"],
                    )
    except Exception:
        app.logger.exception("⚠️ Failed to handle message:")
