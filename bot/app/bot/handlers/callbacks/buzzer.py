import typing

from app.games.services.round import RoundService
from app.users.models import User

if typing.TYPE_CHECKING:
    from app.web.app import Application


async def press_buzzer_callback(
    app: "Application",
    round_id: int,
    callback_id: int,
    user: User,
):
    service: RoundService = RoundService(app)
    try:
        await service.register_buzzer(round_id, user.id)
        await app.telegram.answer_callback_query(callback_id, "Вы первый!")
    except Exception as e:
        await app.telegram.answer_callback_query(callback_id, str(e))
    else:
        return
