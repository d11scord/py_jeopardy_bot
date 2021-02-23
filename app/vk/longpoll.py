import asyncio
import json

from aio_pika import Message
from vk_api.bot_longpoll import VkBotEventType, VkBotMessageEvent

from app.settings import config
from app.vk.accessor import create_vk_connection
from app.vk.utils import bot_call
from app.worker.worker import connect_to_queue


async def send_message_to_queue(channel, event):
    await channel.default_exchange.publish(
        Message(
            body=bytes(event, encoding='utf-8'),
            content_encoding='utf-8',
        ),
        routing_key=config['rabbitmq']['queue_name'],
    )


def parse_event(raw_event: VkBotMessageEvent) -> json:
    event = dict(
        type=raw_event.type.value,  # raw_event.type: VkBotEventType
        from_id=raw_event.object.from_id,
        peer_id=raw_event.object.peer_id,
        text=raw_event.object.text,
    )
    return json.dumps(event)


async def main(loop):
    channel, queue = await connect_to_queue(loop)

    longpoll = create_vk_connection()
    for event in longpoll.listen():
        message_text = event.obj.text
        if (event.type == VkBotEventType.MESSAGE_NEW
            and message_text
            and bot_call in message_text
        ):
            try:
                await send_message_to_queue(
                    channel, parse_event(event)
                )
            except ConnectionResetError as e:
                print(e)
                channel, queue = await connect_to_queue(loop)
            print(f"Sent message ({event.obj.text}) to queue")
        else:
            print('Event type', event.type.value, event)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(main(loop))
    print('Hello from vk bot longpoll')
    loop.run_forever()
