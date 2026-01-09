from unittest.mock import patch

from fastapi import status
from fastapi.testclient import TestClient

from chat_api.app import api
from chat_api.error_contant import ErrorConstant

client = TestClient(api)


@patch("chat_api.chats.chats_views.get")
def test_get_chats_rejects_long_query(mock_get) -> None:
    mock_get.return_value = "5"

    payload = {
        "email": "user@example.com",
        "query": "123456",  # len=6 > MAX_QUERY_LENGTH=5
        "application": "webuddhist",
        "device_type": "web",
        "thread_id": None,
    }
    resp = client.post("/chats", json=payload)

    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.json()["detail"]["error"] == ErrorConstant.BAD_REQUEST
    assert resp.json()["detail"]["message"] == ErrorConstant.MAX_QUERY_LENGTH_ERROR


@patch("chat_api.chats.chats_views.get_chat_stream")
@patch("chat_api.chats.chats_views.get")
def test_get_chats_streaming_success(mock_get, mock_get_chat_stream) -> None:
    mock_get.return_value = "2000"

    async def fake_stream(_chat_request):
        yield b"data: hello\n\n"

    mock_get_chat_stream.return_value = fake_stream(None)

    payload = {
        "email": "user@example.com",
        "query": "hi",
        "application": "webuddhist",
        "device_type": "web",
        "thread_id": None,
    }
    resp = client.post("/chats", json=payload)

    assert resp.status_code == status.HTTP_200_OK
    assert resp.headers["content-type"].startswith("text/event-stream")
    assert b"data: hello" in resp.content


