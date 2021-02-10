import aiohttp
from aiohttp import web
from vk_api.utils import get_random_id


class VkAccessor:
    def __init__(self):
        self.token = None
        self.v = None
        self.group_id = None

    def setup(self, application: web.Application):
        self.token = application["config"]["vk"]["access-token"]
        self.v = application["config"]["vk"]["v"]
        self.group_id = application["config"]["vk"]["group-id"]

        application["vk"] = self

    async def send_message(self, request) -> None:
        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(verify_ssl=False)
        ) as session:
            params = {
                "peer_id": request.object.peer_id,
                "message": request.object.text,
                "random_id": get_random_id(),
                "access_token": self.token,
                "v": self.v,
            }
            async with session.post(
                "https://api.vk.com/method/messages.send",
                params=params,
            ):
                pass
