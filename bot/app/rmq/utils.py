import json

import aio_pika


def parse_json_body(message: aio_pika.IncomingMessage) -> dict:
    try:
        return json.loads(message.body.decode())
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in message body: {e}") from e


def extract_callback_data(payload: dict) -> dict:
    callback_query = payload["callback_query"]
    chat_id = callback_query["message"]["chat"]["id"]
    message_id = callback_query["message"]["message_id"]
    callback_id = callback_query["id"]
    user_data = callback_query["from"]

    data = json.loads(callback_query["data"])
    return {
        "chat_id": chat_id,
        "callback_id": callback_id,
        "message_id": message_id,
        "callback_type": data["type"],
        "game_id": data["game"],
        "round_id": data.get("round"),
        "team": data.get("team"),
        "team_num": data.get("t_num"),
        "user_data": user_data,
    }


def extract_message_data(payload: dict) -> dict:
    msg = payload["message"]
    chat_id = msg["chat"]["id"]
    chat_type = msg["chat"]["type"]
    text = msg.get("text", "")
    user_data = msg.get("from", {})

    command, args = None, ""
    for entity in msg.get("entities", []):
        if entity["type"] == "bot_command":
            command = text[
                entity["offset"] : entity["offset"] + entity["length"]
            ]
            args = text[entity["offset"] + entity["length"] :].strip()
            break

    return {
        "chat_id": chat_id,
        "chat_type": chat_type,
        "user_data": user_data,
        "command": command,
        "args": args,
    }
