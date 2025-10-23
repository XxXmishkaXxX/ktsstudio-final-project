from .client import TelegramBot


def setup_telegram_client(app):
    app.telegram = TelegramBot(app)

    app.on_startup.append(app.telegram.start)
    app.on_cleanup.append(app.telegram.close)


def setup_webhook(app):
    app.bot = TelegramBot(app)

    async def start(_app):
        await app.bot.start()
        try:
            await app.bot.delete_webhook(drop_pending_updates=True)
            await app.bot.set_webhook(app.config.bot.webhook_url)
        except Exception:
            app.logger.exception("⚠️ Failed to setup webhook:")

    async def close(_app):
        await app.bot.close()

    app.on_startup.append(start)
    app.on_cleanup.append(close)
