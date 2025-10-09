import json

import pytest


async def test_healthcheck(client):
    resp = await client.get("/health")
    assert resp.status == 200
    data = await resp.json()
    assert data == {"status": "ok"}


@pytest.mark.asyncio
async def test_webhook_valid_update(client):
    resp = await client.post(
        "/webhook", json={"update_id": 123, "message": {"text": "hi"}}
    )
    assert resp.status == 200
    data = await resp.json()
    assert data == {"status": "ok"}


async def test_webhook_invalid_payload(client):
    resp = await client.post("/webhook", json={"invalid": "data"})
    assert resp.status == 400


@pytest.mark.asyncio
async def test_webhook_publishes(client, mock_rabbitmq, reset_rabbitmq):
    payload = {"update_id": 123, "message": {"text": "Hello"}}
    resp = await client.post("/webhook", json=payload)
    data = await resp.json()

    assert resp.status == 200
    assert data["status"] == "ok"
    mock_rabbitmq.publish.assert_awaited_once_with(message=json.dumps(payload))
