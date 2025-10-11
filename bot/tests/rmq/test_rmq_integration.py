import pytest
import asyncio
import aio_pika
from aio_pika.exceptions import ChannelInvalidStateError


@pytest.mark.asyncio
async def test_rabbitmq_connect(rmq, config):
    await rmq.connect()
    assert rmq.queue is not None
    assert rmq.queue.name == rmq.queue_name or rmq.queue.name == config.rmq.queue


async def test_rabbitmq_consume(rmq):

    await rmq.connect()

    called = asyncio.Event()
    received_body = {}

    async def callback(message: aio_pika.IncomingMessage, app):
        received_body["data"] = message.body.decode()
        called.set()

    await rmq.consume(callback)

    await rmq._channel.default_exchange.publish(
        aio_pika.Message(body=b"ping"),
        routing_key=rmq.queue_name,
    )

    await asyncio.wait_for(called.wait(), timeout=3)

    assert received_body["data"] == "ping"

    await rmq.close()


@pytest.mark.asyncio
async def test_rabbitmq_close_really_closes_connection(rmq):
    """Интеграционный тест: rmq.close() закрывает соединение и делает канал недоступным"""

    await rmq.connect()
    assert not rmq._connection.is_closed
    assert not rmq._channel.is_closed

    await rmq.close()

    assert rmq._connection.is_closed
    assert rmq._channel.is_closed

    with pytest.raises(ChannelInvalidStateError):
        await rmq._channel.default_exchange.publish(
            aio_pika.Message(body=b"after-close"),
            routing_key=rmq.queue_name,
        )