import aiohttp
from aiohttp import web
from vk_api import vk_api
from vk_api.bot_longpoll import VkBotLongPoll


class VkAccessor:
    def __init__(self):
        self.vk_session = None
        self.vk = None
        self.longpoll = None

        self.token = None
        self.v = None
        self.group_id = None

    def setup(self, application: web.Application):
        self.token = application["config"]["vk"]["access-token"]
        self.v = application["config"]["vk"]["v"]
        self.group_id = application["config"]["vk"]["group-id"]

        application["vk"] = self

    def create_vk_connection(self) -> VkBotLongPoll:
        self.vk_session = vk_api.VkApi(token=self.token)
        self.vk = self.vk_session.get_api()
        self.longpoll = VkBotLongPoll(
            self.vk_session, group_id=self.group_id,
        )
        return self.longpoll


async def send_message_to_vk(event, *, token, v, group_id):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            url=f"https://api.vk.com/method/"
                f"messages.send?"
                f"peer_id={event['peer_id']}&"
                f"message={event['text']}&"
                f"access_token={token}&"
                f"v={v}&"
                f"group_id={group_id}",
        ) as resp:
            response = await resp.json()
    return response
