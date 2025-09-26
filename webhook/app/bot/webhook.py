import typing

import aiohttp

if typing.TYPE_CHECKING:
    from app.web.app import Application


class TelegramBot:
    def __init__(self, app: "Application"):
        self.app = app
        self.session: aiohttp.ClientSession | None = None

    async def start(self):
        self.session = aiohttp.ClientSession()

    async def close(self):
        if self.session:
            await self.session.close()

    async def api_call(self, method: str, payload: dict) -> dict:
        url = f"{self.app.config.bot.api_url}/{method}"
        async with self.session.post(url, json=payload) as resp:
            if resp.status != 200:
                text = await resp.text()
                raise Exception(f"Telegram API error {resp.status}: {text}")
            return await resp.json()

    async def set_webhook(self, url: str, **kwargs) -> dict:
        return await self.api_call("setWebhook", {"url": url, **kwargs})


def setup_webhook(app: "Application"):
    app.bot = TelegramBot(app)

    async def start(_app):
        await app.bot.start()
        try:
            await app.bot.set_webhook(app.config.bot.webhook_url)
        except Exception as e:
            app.logger.error(str(e))

    async def close(_app):
        await app.bot.close()

    app.on_startup.append(start)
    app.on_cleanup.append(close)
