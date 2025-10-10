import typing

from db_core.models.rounds import RoundState
from db_core.models.users import User

from app.games.services.round import RoundService

if typing.TYPE_CHECKING:
    from app.web.app import Application


async def answer_command(
    app: "Application",
    chat_id: int,
    chat_type: str,
    answer: str,
    user: User,
):
    if chat_type == "private":
        await app.telegram.send_message(
            chat_id,
            (
                "❌ Команда /ans работает только в групповых чатах.\n"
                "Добавьте бота в чат с друзьями!"
            ),
        )
        return

    game = await app.store.games.is_active_game_in_chat(chat_id)
    if not game:
        return

    service: RoundService = RoundService(app)

    game_id = game.id
    state = await app.store.rounds.get_round_state(game.current_round_id)

    if state == RoundState.buzzer_answer:
        await service.buzzer_answer_question(game_id, user.id, answer)

    elif state == RoundState.team_play:
        await service.team_answer_question(game_id, chat_id, user.id, answer)
    return
