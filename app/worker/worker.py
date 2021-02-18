import asyncio
import json

from aio_pika import connect, IncomingMessage

from app.settings import config
from app.vk.accessor import VkAccessor


async def on_message(message: IncomingMessage):
    print(" [x] Received message %r" % message)
    event = json.loads(message.body.decode('utf-8'))
    print("Message body is: %r" % message.body, )
    # TODO: не работает
    response = await VkAccessor().send_message(event=event)
    print('response', response)
    message.ack()


async def main(loop):
    print('Perform connection')
    connection = await connect(
        url=config['rabbitmq']['url'], loop=loop
    )
    print('Creating a channel')
    channel = await connection.channel()
    print('Declaring queue')
    queue = await channel.declare_queue(
        name=config['rabbitmq']['queue_name'], durable=True,
    )

    print('listen')
    await queue.consume(on_message)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main(loop))

    print(" [*] Waiting for messages. To exit press CTRL+C")
    loop.run_forever()
