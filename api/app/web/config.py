import typing
from dataclasses import dataclass

import yaml

if typing.TYPE_CHECKING:
    from app.web.app import Application


@dataclass
class ServerConfig:
    host: str = "0.0.0.0"
    port: int = 8082


@dataclass
class SessionConfig:
    key: str


@dataclass
class AdminConfig:
    email: str = "admin@admin.ru"
    password: str = "password"


@dataclass
class DBConfig:
    host: str = "localhost"
    port: int = 5432
    user: str = "postgres"
    password: str = ""
    database: str = ""


@dataclass
class Config:
    server: ServerConfig
    admin: AdminConfig
    db: DBConfig
    session: SessionConfig | None = None


def setup_config(app: "Application", config_path: str):
    with open(config_path, "r") as f:
        raw = yaml.safe_load(f)

    server_conf = raw.get("server", {})
    db_conf = raw.get("database", {})
    admin_conf = raw.get("admin", {})
    session_conf = raw.get("session", {})

    server = ServerConfig(
        host=server_conf.get("host", "0.0.0.0"),
        port=server_conf.get("port", 8080),
    )

    session = SessionConfig(
        key=session_conf.get("key"),
    )
    db = DBConfig(
        host=db_conf.get("host", "localhost"),
        port=db_conf.get("port", 5432),
        user=db_conf.get("user", "postgres"),
        password=db_conf.get("password", ""),
        database=db_conf.get("database", ""),
    )

    admin = AdminConfig(
        email=admin_conf.get("email", "admin@admin.ru"),
        password=admin_conf.get("password", "password"),
    )
    app.config = Config(server=server, db=db, admin=admin, session=session)
