from unittest.mock import AsyncMock, MagicMock

import pytest
from db_core.models.users import State, User


@pytest.fixture
def mocked_app():
    app = MagicMock()

    # Telegram
    app.telegram.send_message = AsyncMock()

    # Logger
    app.logger = MagicMock()

    # Config
    app.config.bot.username = "TestBot"

    # Game store
    app.store.games.is_active_game_in_chat = AsyncMock()

    # Round store
    app.store.rounds.get_round_state = AsyncMock()

    # Round service
    app.round_service = MagicMock()
    app.round_service.buzzer_answer_question = AsyncMock()
    app.round_service.team_answer_question = AsyncMock()

    # Game service
    app.game_service = MagicMock()
    app.game_service.create_game = AsyncMock()
    app.game_service.get_user_created_game = AsyncMock()
    app.game_service.stop_game = AsyncMock()

    return app


@pytest.fixture
def creator_user():
    return User(id=7, username="creator", state=State.in_game)


@pytest.fixture
def not_creator_user():
    return User(id=5, username="not_creator", state=State.in_game)


@pytest.fixture
def private_user():
    user = MagicMock()
    user.username = "test_user"
    return user


@pytest.fixture
def group_user():
    user = MagicMock()
    user.username = "group_user"
    return user


@pytest.fixture
def idle_user():
    user = MagicMock()
    user.username = "player1"
    user.state = State.idle
    user.id = 42
    return user


@pytest.fixture
def in_game_user():
    user = MagicMock()
    user.username = "player2"
    user.state = State.in_game
    user.id = 43
    return user
