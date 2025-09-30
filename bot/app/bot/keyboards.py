def main_menu(bot_username: str) -> dict:
    return {
        "inline_keyboard": [
            [
                {
                    "text": "➕ Добавить бота",
                    "url": f"https://t.me/{bot_username}?startgroup=true",
                }
            ],
        ]
    }


def join_game(game_id):
    return {
        "inline_keyboard": [
            [
                {
                    "text": "🚪 Присоединиться",
                    "callback_data": f"join:{game_id}",
                }
            ],
        ]
    }
