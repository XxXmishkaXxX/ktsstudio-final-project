from aiohttp import web

routes = web.RouteTableDef()


@routes.post("/webhook")
async def webhook(request: web.Request):
    data = await request.json()
    app = request.app
    app.logger.info(data)

    return web.Response(status=200)
