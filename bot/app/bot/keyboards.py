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
