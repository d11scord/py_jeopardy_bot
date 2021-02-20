import asyncio
import json

from aio_pika import connect, IncomingMessage

from app.game.bot.bot import JeopardyBot
from app.settings import config


bot = JeopardyBot()


async def on_message(message: IncomingMessage):
    print(" [x] Received message")
    event = json.loads(message.body.decode('utf-8'))
    print("Message body is:", message.body)
    await bot.check_message(event)
    message.ack()


async def connect_to_queue(loop):
    connection = await connect(
        url=config['rabbitmq']['url'], loop=loop,
    )
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=1)
    queue = await channel.declare_queue(
        name=config['rabbitmq']['queue_name'], durable=True,
    )
    return channel, queue


async def main(loop):
    print(' [x] Perform connection')
    channel, queue = await connect_to_queue(loop)
    await queue.consume(on_message, no_ack=False)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main(loop))
    print(" [*] Waiting for messages. To exit press CTRL+C")
    loop.run_forever()
