from aiohttp import web
from vk_api import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
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

    async def listen_to_messages(self):
        print('Hello from longpoll')
        vk_session = vk_api.VkApi(token=self.token)
        vk = vk_session.get_api()
        longpoll = VkBotLongPoll(vk_session, group_id=self.group_id)

        for event in longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                print('Got message from VK')
                vk.messages.send(
                    random_id=get_random_id(),
                    peer_id=event.obj.peer_id,
                    message=event.obj.text,
                )
