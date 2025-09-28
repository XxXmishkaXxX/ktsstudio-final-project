import typing

if typing.TYPE_CHECKING:
    from app.web.app import Application


async def play_command(
    app: "Application",
    chat_id: int,
    user_data: dict,
    chat_type: str,
):
    if chat_type == "private":
        await app.telegram.send_message(
            chat_id,
            (
                "❌ Команда /play работает только в групповых чатах.\n"
                "Добавьте бота в чат с друзьями!"
            ),
        )
        return

    await app.telegram.send_message(
        chat_id,
        f"🎮 Пользователь @{user_data.get('username', user_data['id'])} "
        "запустил игру!",
    )
