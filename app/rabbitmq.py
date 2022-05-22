import json

import aio_pika

RABBITMQ_URL = "amqp://guest:guest@rabbitmq/"


async def publish_message(message, routing_key):
    connection = await aio_pika.connect_robust(
        "amqp://guest:guest@rabbitmq/",
    )

    async with connection:
        channel = await connection.channel()

        await channel.default_exchange.publish(
            aio_pika.Message(body=json.dumps(message).encode()),
            routing_key=routing_key,
        )


async def get_message(queue_name):
    connection = await aio_pika.connect_robust(RABBITMQ_URL)

    async with connection:
        # Creating channel
        channel = await connection.channel()

        # Will take no more than 10 messages in advance
        await channel.set_qos(prefetch_count=10)

        # Declaring queue
        queue = await channel.declare_queue(queue_name, auto_delete=True)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    yield json.loads(message.body.decode())
