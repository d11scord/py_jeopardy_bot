from aiohttp import web


@web.middleware
async def error_middleware(request, handler):
    try:
        return await handler(request)
    except web.HTTPException as ex:
        return web.json_response(
            status=ex.status, data={"code": ex.reason.lower()}
        )
    except Exception as e:
        request.app.logger.exception("Exception: {}".format(str(e)), exc_info=e)
        return web.json_response(status=500, data={"code": "internal_error"})
