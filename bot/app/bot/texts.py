from html import escape


def welcome_message(username: str) -> str:
    return (
        f"👋 Привет, {username}!\n\n"
        "Я — бот для игры «100 к 1» 🎮\n"
        "Добавьте меня в чат с друзьями, чтобы сыграть вместе!\n\n"
        "📌 Как играть:\n"
        "— Я задам вопрос, на который уже отвечали 100 человек.\n"
        "— Ваша задача — угадывать самые популярные ответы.\n"
        "— Команда, которая наберёт больше очков,\n"
        "  побеждает!\n\n"
        "✨ Зовите друзей в чат, запускайте игру и проверяйте,\n"
        "  кто мыслит как большинство!"
    )


def get_game_text(team_1, team_2, state="created", extra=""):
    states_text = {
        "created": "⏳ Ожидание игроков...",
        "starting": "🚀 Старт игры!",
        "in_progress": "🎮 Играем!",
        "finished": "🎉 Игра окончена!",
    }

    state_message = states_text.get(state, "⏳ Ожидание игроков...")

    team1_text = "🟢 Команда 1\n" + "\n".join(
        f"{i + 1}️⃣ {name}" for i, name in enumerate(team_1)
    )
    team2_text = "🔵 Команда 2\n" + "\n".join(
        f"{i + 1}️⃣ {name}" for i, name in enumerate(team_2)
    )

    return (
        f"🎲 <b>Игра: 100 к 1</b> 🎲\n\n"
        f"<b>Состояние игры:</b>\n<b>{escape(state_message)}</b>\n\n"
        f"{escape(team1_text)}\n\n{escape(team2_text)}"
    )
