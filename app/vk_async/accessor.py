import json

from aio_pika import Message, connect, DeliveryMode
from aiohttp import web
import aiohttp


class VkAccessor:
    def __init__(self):
        # tokens
        self.v = None
        self.token = None
        self.group_id = None
        # vk session
        self.key = None
        self.server = None
        self.ts = None
        self.wait = 25

        self.MESSAGE_NEW = 'message_new'

    def setup(self, application: web.Application):
        self.token = application["config"]["vk"]["access-token"]
        self.v = application["config"]["vk"]["v"]
        self.group_id = application["config"]["vk"]["group-id"]

        application["vk"] = self

    async def listen_to_messages(self):
        print('Hello from vk bot longpoll')
        async for events in self.listen():
            for event in events:
                if event['type'] == self.MESSAGE_NEW:
                    print(f'Sending message ((({event["text"]}))) to queue')
                    await self.send_message_to_queue(event)
                else:
                    print('error', event)

    async def listen(self):
        await self.update_longpoll_server()
        while True:
            event = await self.check()
            yield event

    async def update_longpoll_server(self, update_ts=True):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    url=f"https://api.vk.com/method/"
                        f"groups.getLongPollServer?"
                        f"access_token={self.token}&"
                        f"v={self.v}&"
                        f"group_id={self.group_id}",
                    verify_ssl=False,
            ) as resp:
                response = await resp.json()

        print('prepare', response)
        body = response.get('response')
        self.key = body.get('key')
        self.server = body.get('server')

        if update_ts:
            self.ts = body.get('ts')

    async def check(self) -> list:
        async with aiohttp.ClientSession() as session:
            # https://vk.com/dev/bots_longpoll
            async with session.get(
                    url=f"{self.server}?act=a_check&"
                        f"key={self.key}&"
                        f"ts={self.ts}&"
                        f"wait={self.wait}",
                    verify_ssl=False,
                    timeout=self.wait + 10,
            ) as resp:
                response = await resp.json()

        print('check', response)

        if 'failed' not in response:
            self.ts = response['ts']
            return [
                self.parse_event(raw_event)
                for raw_event in response['updates']
            ]

        elif response['failed'] == 1:
            self.ts = response['ts']

        elif response['failed'] == 2:
            await self.update_longpoll_server(update_ts=False)

        elif response['failed'] == 3:
            await self.update_longpoll_server()

        return []

    @staticmethod
    def parse_event(raw_event: dict) -> dict:
        event = dict(
            type=raw_event.get('type'),
            from_id=raw_event['object'].get('from_id'),
            peer_id=raw_event['object'].get('peer_id'),
            text=raw_event['object'].get('text'),
            event_id=raw_event.get('event_id'),
        )
        return event

    async def send_message_to_queue(self, message: dict):
        message.update({
            'access_token': self.token,
            'v': self.v,
            'group_id': self.group_id,
        })
        message = json.dumps(message)

        connection = await connect(
            "amqp://guest:guest@localhost/",
        )
        channel = await connection.channel()
        await channel.default_exchange.publish(
            Message(
                bytes(message, encoding='utf-8'),
                content_encoding='utf-8',
                # Delivery mode 2 makes the broker save the message to disk.
                delivery_mode=DeliveryMode.PERSISTENT,
            ),
            routing_key="vkbot_test3",
        )
        print(f"Sent message ((({message}))) to queue")
        await connection.close()
