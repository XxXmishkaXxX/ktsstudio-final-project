import yaml
from app.web.config import Config, setup_config


def test_config_loads_correctly(tmp_path):
    config_file = tmp_path / "config_test.yaml"
    config_file.write_text(
        yaml.dump(
            {
                "bot": {"token": "12345", "webhook_url": "https://example.com"},
                "server": {"host": "127.0.0.1", "port": 9090},
            }
        )
    )

    class DummyApp:
        pass

    app = DummyApp()
    setup_config(app, str(config_file))

    assert isinstance(app.config, Config)
    assert app.config.bot.token == "12345"
    assert app.config.bot.api_url == "https://api.telegram.org/bot12345"
    assert app.config.server.port == 9090
