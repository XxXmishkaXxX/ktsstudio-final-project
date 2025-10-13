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
                        {
                            "type": "join",
                            "game": game_id,
                            "team": team1_id,
                            "t_num": 1,
                        }
                    ),
                }
            ],
            [
                {
                    "text": "🚪 Присоединиться в команду 2",
                    "callback_data": json.dumps(
                        {
                            "type": "join",
                            "game": game_id,
                            "team": team2_id,
                            "t_num": 2,
                        }
                    ),
                }
            ],
        ]
    }


def leave_game(game_id: int):
    return {
        "inline_keyboard": [
            [
                {
                    "text": "Выйти из игры",
                    "callback_data": json.dumps(
                        {"type": "leave", "game": game_id}
                    ),
                }
            ]
        ]
    }


def buzzer_button(game_id: int, round_id: int) -> dict:
    return {
        "inline_keyboard": [
            [
                {
                    "text": "🛑",
                    "callback_data": json.dumps(
                        {"type": "buzzer", "game": game_id, "round": round_id}
                    ),
                }
            ],
        ]
    }
