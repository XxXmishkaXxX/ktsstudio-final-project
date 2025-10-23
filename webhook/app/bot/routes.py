import json

from aiohttp import web

routes = web.RouteTableDef()


@routes.post("/webhook")
async def webhook(request: web.Request):
    try:
        data = await request.json()
    except Exception:
        return web.json_response({"error": "invalid json"}, status=400)

    if not data or "update_id" not in data:
        return web.json_response({"error": "invalid payload"}, status=400)

    app = request.app

    try:
        await app.rmq.publish(message=json.dumps(data))
        app.logger.info("Message published to RabbitMQ")
    except Exception as e:
        app.logger.error("Failed to publish message: %s", e)
        return web.json_response({"error": "failed to publish"}, status=500)

    return web.json_response({"status": "ok"}, status=200)
