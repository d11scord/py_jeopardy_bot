import asyncio
import json

import aiohttp
from aio_pika import connect, IncomingMessage


async def on_message(message: IncomingMessage):
    print(" [x] Received message %r" % message)
    body = json.loads(message.body)
    print("Message body is: %r" % body)
    async with aiohttp.ClientSession() as session:
        async with session.get(
                url=f"https://api.vk.com/method/"
                    f"messages.send?"
                    f"peer_id={body['peer_id']}&"
                    f"message={body['text']}&"
                    f"access_token={body['access_token']}&"
                    f"v={body['v']}"
                    f"group_id={body['group_id']}",
                verify_ssl=False,
        ) as resp:
            response = await resp.json()

    print('response', response)
    message.ack()


async def main(loop):
    print('Perform connection')
    connection = await connect(
        "amqp://guest:guest@localhost/", loop=loop
    )

    print('Creating a channel')
    channel = await connection.channel()

    print('Declaring queue')
    queue = await channel.declare_queue("vkbot_test3", durable=True)

    print('listen')
    await queue.consume(on_message)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main(loop))

    # we enter a never-ending loop that waits for data and
    # runs callbacks whenever necessary.
    print(" [*] Waiting for messages. To exit press CTRL+C")
    loop.run_forever()
