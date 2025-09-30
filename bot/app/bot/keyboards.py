import json


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


def join_game(game_id: int, team1_id: int, team2_id: int):
    return {
        "inline_keyboard": [
            [
                {
                    "text": "🚪 Присоединиться в команду 1",
                    "callback_data": json.dumps(
                        {"t": "join", "g": game_id, "team": team1_id}
                    ),
                }
            ],
            [
                {
                    "text": "🚪 Присоединиться в команду 2",
                    "callback_data": json.dumps(
                        {"t": "join", "g": game_id, "team": team2_id}
                    ),
                }
            ],
        ]
    }
