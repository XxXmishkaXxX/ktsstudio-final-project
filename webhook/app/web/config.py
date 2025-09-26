from dataclasses import dataclass
import typing
import yaml

if typing.TYPE_CHECKING:
    from app.web.app import Application


@dataclass
class BotConfig:
    token: str
    webhook_url: str
    api_url: str = ""


@dataclass
class ServerConfig:
    host: str = "0.0.0.0"
    port: int = 8080


@dataclass
class RMQConfig:
    host: str = "localhost"
    port: int = 5672
    user: str = "guest"
    password: str = "guest"
    queue: str = "bot_events"


@dataclass
class Config:
    bot: BotConfig
    server: ServerConfig
    rmq: RMQConfig


def setup_config(app: "Application", config_path: str):
    with open(config_path, "r") as f:
        raw = yaml.safe_load(f)

    bot_conf = raw.get("bot", {})
    server_conf = raw.get("server", {})
    rmq_conf = raw.get("rabbitmq", {})

    bot = BotConfig(
        token=bot_conf.get("token", ""),
        webhook_url=bot_conf.get("webhook_url", "")
    )
    bot.api_url = f"https://api.telegram.org/bot{bot.token}"

    server = ServerConfig(
        host=server_conf.get("host", "0.0.0.0"),
        port=server_conf.get("port", 8080)
    )

    rmq = RMQConfig(
        host=rmq_conf.get("host", "localhost"),
        port=rmq_conf.get("port", 5672),
        user=rmq_conf.get("user", "guest"),
        password=rmq_conf.get("password", "guest"),
        queue=rmq_conf.get("queue", "bot_events"),
    )

    app.config = Config(
        bot=bot,
        server=server,
        rmq=rmq,
    )
