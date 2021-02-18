import json

from aio_pika import Message, DeliveryMode, connect
from aiohttp import web
from vk_api.bot_longpoll import VkBotEventType, VkBotMessageEvent


class LongPoll:
    def __init__(self):
        self.longpoll = None
        # rabbit
        self.connection = None
        self.channel = None
        self.url = None
        self.queue_name = None

    def setup(self, application: web.Application):
        self.url = application["config"]["rabbitmq"]["url"]
        self.queue_name = application["config"]["rabbitmq"]["queue_name"]

        application.on_startup.append(self.on_startup)

    async def on_startup(self, application: web.Application):
        await self.connect_to_queue()
        self.longpoll = application['vk'].create_vk_connection()
        application["longpoll"] = self

        await self.listen()

    async def listen(self):
        print('Hello from vk bot longpoll')

        for event in self.longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW and event.obj.text:
                print('Got message from VK')
                await self.send_message_to_queue(
                    self.parse_event(event)
                )
                print(f"Sent message ({event.obj.text}) to queue")
            else:
                print('Event type', event.type.value, event)

    @staticmethod
    def parse_event(raw_event: VkBotMessageEvent) -> json:
        event = dict(
            type=raw_event.type.value,  # raw_event.type: VkBotEventType
            from_id=raw_event.object.from_id,
            peer_id=raw_event.object.peer_id,
            text=raw_event.object.text,
        )
        return json.dumps(event)

    async def send_message_to_queue(self, event: json):
        await self.channel.default_exchange.publish(
            Message(
                bytes(event, encoding='utf-8'),
                content_encoding='utf-8',
                # Delivery mode 2 makes the broker save the message to disk
                delivery_mode=DeliveryMode.PERSISTENT,
            ),
            routing_key=self.queue_name,
        )

    async def connect_to_queue(self):
        self.connection = await connect(
            url=self.url,
        )
        self.channel = await self.connection.channel()
