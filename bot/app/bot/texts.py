from html import escape

from app.games.models.teams import Team


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


def get_game_created_text(team_1, team_2, extra=""):
    state_message = "⏳ Ожидание игроков..."

    team1_text = "🟢 Команда 1\n" + "\n".join(
        f"{i + 1}️⃣ {name}" for i, name in enumerate(team_1)
    )
    team2_text = "🔵 Команда 2\n" + "\n".join(
        f"{i + 1}️⃣ {name}" for i, name in enumerate(team_2)
    )

    return (
        f"🎲 <b>Игра: 100 к 1</b> 🎲\n\n"
        f"<b>{escape(state_message)}</b>\n\n"
        f"{escape(team1_text)}\n\n{escape(team2_text)}\n\n"
        f"{escape(extra)}"
    )


def get_game_round_buzzers_text(
    round_num: int,
    round_question: str,
    sec: int,
    buzzers: list[str] | None = None,
    player: str | None = None,
    opened_answers: list[str] | None = None,
):
    text_lines = []

    header = (
        "🎲 <b>Игра: 100 к 1</b> 🎲\n\n"
        f"<b>🎯 Раунд №{round_num}</b>\n"
        "🔥 <b>Дуэль 1 на 1</b> 🔥\n"
        "<b>🎮 Играем!</b>\n\n"
    )
    text_lines.append(header)

    if buzzers:
        text_lines.append("<b>⚡ На баззере:</b>")
        text_lines.append(" VS ".join(buzzers) + "\n")

    text_lines.append(f"\n<b>❓ Вопрос:</b> {round_question}\n")

    text_lines.append("<b>Ответы</b>\n")
    table = [
        "1. ⬜️⬜️⬜️⬜️",
        "2. ⬜️⬜️⬜️⬜️",
        "3. ⬜️⬜️⬜️⬜️",
        "4. ⬜️⬜️⬜️⬜️",
        "5. ⬜️⬜️⬜️⬜️",
    ]
    if opened_answers:
        for ans in opened_answers:
            table[ans.answer_option.position - 1] = (
                f"{ans.answer_option.position}."
                f"{ans.answer_option.text}"
                f"{ans.answer_option.points}"
            )

    text_lines.append("\n".join(table) + "\n")
    if player:
        text_lines.append(f"🔥{player} отвечает на вопрос!\n")
    text_lines.append(f"\n<b>⏱ Осталось:</b> {sec} сек.")

    return "".join(text_lines)


def get_game_round_teamplay_text(
    round_num: int,
    round_question: str,
    score: int,
    count_strikes: int,
    team: Team,
    sec: int,
    opened_answers: list[dict] | None = None,  # теперь список словарей
):
    text_lines = []

    header = (
        "<b>🎲 Игра: 100 к 1 🎲</b>\n\n"
        f"<b>🎯 Раунд №{round_num}</b>\n"
        "<b>🚀 Очередь команды!</b>\n"
        "<b>🎮 Играем!</b>\n\n"
    )
    text_lines.append(header)

    text_lines.append(f"<b>💰 Очки: {score} </b>\n")
    text_lines.append(f"<b>❓ Вопрос:</b> {round_question}\n")

    text_lines.append("<b>Ответы</b>\n")
    table = [
        "1. ⬜️⬜️⬜️⬜️",
        "2. ⬜️⬜️⬜️⬜️",
        "3. ⬜️⬜️⬜️⬜️",
        "4. ⬜️⬜️⬜️⬜️",
        "5. ⬜️⬜️⬜️⬜️",
    ]

    if opened_answers:
        for ans in opened_answers:
            pos = ans["position"] - 1
            table[pos] = f"{ans['position']}. {ans['text']} {ans['points']}"

    text_lines.append("\n".join(table) + "\n")

    team_text = "🟢 <b>Команда</b>\n" + "\n".join(
        f"{i + 1}️⃣ {member.user.username}"
        for i, member in enumerate(team.members)
    )
    text_lines.append(team_text)

    text_strikes = "<b>\nПромахи: </b>" + "❌" * count_strikes + "\n"
    text_lines.append(text_strikes)

    text_lines.append(f"\n<b>⏱ Осталось:</b> {sec} сек.")

    return "".join(text_lines)


def get_finish_game_text(
    winners: list[str] | None = None, score: int | None = None
):
    text_lines = []

    header = "🎲 <b>Игра: 100 к 1</b> 🎲\n\n<b>🏁 Игра окончена!</b>\n\n"

    if winners:
        team_text = "🏆 <b>Победила команда:</b>\n"
        team_text += "🟢 Команда\n" + "\n".join(
            f"{i + 1}️⃣ {name}" for i, name in enumerate(winners)
        )

        if score is not None:
            score_text = f"\n\n<b>Очки:</b> {score}"
        else:
            score_text = ""

        text_lines.append(header + team_text + score_text)

    else:
        draw_text = (
            header
            + "🤝 <b>Ничья!</b>\nОбе команды показали отличный результат!"
        )
        text_lines.append(draw_text)

    return "\n".join(text_lines)
