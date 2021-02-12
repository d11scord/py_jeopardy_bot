from aiohttp import web
from vk_api import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType, VkBotMessageEvent
from vk_api.utils import get_random_id


class VkAccessor:
    def __init__(self):
        self.v = None
        self.token = None
        self.group_id = None

        self.vk = None
        self.longpoll = None

    def setup(self, application: web.Application):
        self.token = application["config"]["vk"]["access-token"]
        self.v = application["config"]["vk"]["v"]
        self.group_id = application["config"]["vk"]["group-id"]

        application["vk"] = self

    def listen_to_messages(self):
        print('Hello from vk bot longpoll')
        vk_session = vk_api.VkApi(token=self.token)
        self.vk = vk_session.get_api()
        self.longpoll = VkBotLongPoll(vk_session, group_id=self.group_id)

        for event in self.longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW and event.obj.text:
                print('Got message from VK')
                self.send_message(event)

    def send_message(self, event: VkBotMessageEvent) -> None:
        # TODO: add rabbitmq
        self.vk.messages.send(
            random_id=get_random_id(),
            peer_id=event.obj.peer_id,
            message=event.obj.text,
        )

