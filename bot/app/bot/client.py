import asyncio
import json
import re
import typing
import aiohttp

from aiohttp import ClientError, ServerDisconnectedError

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
        timeout = aiohttp.ClientTimeout(total=5, connect=3)  # ⏱️ ограничение ожидания
        max_attempts = 3

        for attempt in range(1, max_attempts + 1):
            try:
                self.app.logger.info(f"[API_CALL] -> {method}, attempt {attempt}")
                async with self.session.post(url, json=payload, timeout=timeout) as resp:
                    self.app.logger.info(f"[API_CALL] <- {method}, status={resp.status}")

                    # Проверяем статус
                    if resp.status != 200:
                        text = await resp.text()
                        self.app.logger.warning(f"Telegram API error {resp.status}: {text}")

                        if resp.status == 429:  # rate limit
                            await asyncio.sleep(5)
                            continue

                        raise Exception(f"Telegram API error {resp.status}: {text}")

                    # Успешный ответ
                    return await resp.json()

            except (ServerDisconnectedError, aiohttp.ServerTimeoutError, asyncio.TimeoutError) as e:
                self.app.logger.warning(f"Server disconnected/timeout on {method}: {e}")
                # 🧩 Пересоздаём сессию, если соединение порвалось
                try:
                    await self.session.close()
                except Exception:
                    pass
                self.session = aiohttp.ClientSession()

                if attempt < max_attempts:
                    await asyncio.sleep(1 * attempt)
                    continue
                else:
                    raise

            except ClientError as e:
                self.app.logger.warning(f"ClientError on {method}: {e}")
                if attempt < max_attempts:
                    await asyncio.sleep(1 * attempt)
                    continue
                else:
                    raise

            except Exception as e:
                self.app.logger.exception(f"Unexpected error in api_call: {e}")
                if attempt < max_attempts:
                    await asyncio.sleep(1 * attempt)
                    continue
                else:
                    raise

        # Если после всех попыток не удалось — возвращаем пустой результат
        return {}


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
