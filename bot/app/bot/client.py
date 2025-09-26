import json
import typing

import aiohttp

if typing.TYPE_CHECKING:
    from app.web.app import Application


class TelegramBot:
    def __init__(self, app: "Application"):
        self.app = app
        self.session: aiohttp.ClientSession | None = None

    async def start(self, _app=None):
        self.session = aiohttp.ClientSession()

    async def close(self, _app=None):
        if self.session:
            await self.session.close()

    async def api_call(self, method: str, payload: dict) -> dict:
        url = f"{self.app.config.bot.api_url}/{method}"
        async with self.session.post(url, json=payload) as resp:
            if resp.status != 200:
                text = await resp.text()
                raise Exception(f"Telegram API error {resp.status}: {text}")
            return await resp.json()

    async def send_message(self, chat_id: int, text: str, **kwargs) -> dict:
        return await self.api_call(
            "sendMessage", {"chat_id": chat_id, "text": text, **kwargs}
        )

    async def delete_message(self, chat_id: int, message_id: int) -> dict:
        return await self.api_call(
            "deleteMessage", {"chat_id": chat_id, "message_id": message_id}
        )

    async def edit_message(
        self, chat_id: int, message_id: int, text: str | None = None, **kwargs
    ) -> dict:
        return await self.api_call(
            "editMessageText",
            {
                "chat_id": chat_id,
                "message_id": message_id,
                "text": text,
                **kwargs,
            },
        )

    async def edit_message_reply_markup(
        self, chat_id: int, message_id: int, reply_markup: dict | None = None
    ) -> dict:
        payload = {"chat_id": chat_id, "message_id": message_id}
        if reply_markup is not None:
            payload["reply_markup"] = (
                json.dumps(reply_markup)
                if isinstance(reply_markup, dict)
                else reply_markup
            )
        return await self.api_call("editMessageReplyMarkup", payload)

    async def answer_callback_query(
        self,
        callback_query_id: int,
        text: str | None = None,
        show_alert: bool = False,
    ) -> dict:
        payload = {"callback_query_id": callback_query_id}

        if text is not None:
            payload["text"] = text
        if show_alert:
            payload["show_alert"] = True
        return await self.api_call("answerCallbackQuery", payload)


def setup_telegram_client(app: "Application"):
    app.telegram = TelegramBot(app)

    app.on_startup.append(app.telegram.start)
    app.on_cleanup.append(app.telegram.close)
