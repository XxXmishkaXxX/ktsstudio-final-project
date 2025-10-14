import typing
from dataclasses import dataclass

import yaml

if typing.TYPE_CHECKING:
    from app.web.app import Application


@dataclass
class BotConfig:
    token: str
    username: str
    api_url: str = ""


@dataclass
class ServerConfig:
    host: str = "0.0.0.0"
    port: int = 8081


@dataclass
class RMQConfig:
    host: str = "localhost"
    port: int = 5672
    user: str = "guest"
    password: str = "guest"
    queue: str = "bot_events"


@dataclass
class RedisConfig:
    url: str = "redis://localhost:6379/0"


@dataclass
class DBConfig:
    host: str = "localhost"
    port: int = 5432
    user: str = "postgres"
    password: str = ""
    database: str = ""


@dataclass
class Game:
    min_players: int = 5
    max_players: int = 5


@dataclass
class Config:
    bot: BotConfig
    server: ServerConfig
    rmq: RMQConfig
    redis: RedisConfig
    db: DBConfig
    game: Game


def setup_config(app: "Application", config_path: str):
    with open(config_path, "r") as f:
        raw = yaml.safe_load(f)

    bot_conf = raw.get("bot", {})
    server_conf = raw.get("server", {})
    game_conf = raw.get("game", {})
    rmq_conf = raw.get("rabbitmq", {})
    redis_conf = raw.get("redis", {})
    db_conf = raw.get("database", {})

    bot = BotConfig(
        token=bot_conf.get("token", ""),
        username=bot_conf.get("username"),
        api_url=f"https://api.telegram.org/bot{bot_conf.get('token', '')}",
    )

    server = ServerConfig(
        host=server_conf.get("host", "0.0.0.0"),
        port=server_conf.get("port", 8080),
    )

    game = Game(
        min_players=game_conf.get("min_players"),
        max_players=game_conf.get("max_players"),
    )

    rmq = RMQConfig(
        host=rmq_conf.get("host", "localhost"),
        port=rmq_conf.get("port", 5672),
        user=rmq_conf.get("user", "guest"),
        password=rmq_conf.get("password", "guest"),
        queue=rmq_conf.get("queue", "bot_events"),
    )

    redis = RedisConfig(url=redis_conf.get("url", "redis://localhost:6379/0"))

    db = DBConfig(
        host=db_conf.get("host", "localhost"),
        port=db_conf.get("port", 5432),
        user=db_conf.get("user", "postgres"),
        password=db_conf.get("password", ""),
        database=db_conf.get("database", ""),
    )

    app.config = Config(
        bot=bot, server=server, rmq=rmq, redis=redis, db=db, game=game
    )
