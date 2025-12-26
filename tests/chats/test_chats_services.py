import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from chat_api.chats.chats_reponse_model import ChatRequest
from chat_api.chats.chats_services import sse_frame_from_line, get_chat_stream
from chat_api.threads.models import DeviceType


def _sessionlocal_cm(session):
    cm = MagicMock()
    cm.__enter__.return_value = session
    cm.__exit__.return_value = False
    return cm


def test_sse_frame_from_line_empty_line_returns_none() -> None:
    assert sse_frame_from_line("") is None
    assert sse_frame_from_line("   ") is None


def test_sse_frame_from_line_comment_line() -> None:
    assert sse_frame_from_line(":keep-alive") == b":keep-alive\n\n"


def test_sse_frame_from_line_data_line_json() -> None:
    collected = []
    frame = sse_frame_from_line('data: {"x": 1}', on_json=collected.append)
    assert frame == b'data: {"x": 1}\n\n'
    assert collected == [{"x": 1}]


@patch("chat_api.chats.chats_services.save_chat")
@patch("chat_api.chats.chats_services.SessionLocal")
@patch("chat_api.chats.chats_services.create_thread")
@patch("chat_api.chats.chats_services.httpx.AsyncClient")
def test_get_chat_stream_creates_thread_and_persists_chat(
    mock_async_client, mock_create_thread, mock_sessionlocal, mock_save_chat
) -> None:
    thread_id = uuid4()
    mock_create_thread.return_value = MagicMock(id=thread_id)

    # Mock httpx streaming response: a single JSON line -> chat_list has 1 item
    stream_response = MagicMock()

    async def _aiter_lines():
        yield 'data: {"role":"assistant","content":"hello"}'

    stream_response.aiter_lines = _aiter_lines

    stream_cm = MagicMock()
    stream_cm.__aenter__ = AsyncMock(return_value=stream_response)
    stream_cm.__aexit__ = AsyncMock(return_value=False)

    client_instance = MagicMock()
    client_instance.stream.return_value = stream_cm

    client_cm = MagicMock()
    client_cm.__aenter__ = AsyncMock(return_value=client_instance)
    client_cm.__aexit__ = AsyncMock(return_value=False)
    mock_async_client.return_value = client_cm

    db_session = MagicMock()
    mock_sessionlocal.return_value = _sessionlocal_cm(db_session)

    chat_request = ChatRequest(
        email="user@example.com",
        query="hi",
        application="webuddhist",
        device_type=DeviceType.web.value,
        thread_id=None,
    )

    async def _collect():
        return [chunk async for chunk in get_chat_stream(chat_request)]

    chunks = asyncio.run(_collect())

    # Final chunk should include the thread_id that was created
    assert any(str(thread_id).encode("utf-8") in c for c in chunks)
    mock_create_thread.assert_called_once()
    mock_sessionlocal.assert_called_once()
    mock_save_chat.assert_called_once()


@patch("chat_api.chats.chats_services.save_chat")
@patch("chat_api.chats.chats_services.SessionLocal")
@patch("chat_api.chats.chats_services.create_thread")
@patch("chat_api.chats.chats_services.httpx.AsyncClient")
def test_get_chat_stream_uses_existing_thread_id(
    mock_async_client, mock_create_thread, mock_sessionlocal, mock_save_chat
) -> None:
    existing_thread_id = str(uuid4())

    stream_response = MagicMock()

    async def _aiter_lines():
        yield 'data: {"role":"assistant","content":"hello"}'

    stream_response.aiter_lines = _aiter_lines

    stream_cm = MagicMock()
    stream_cm.__aenter__ = AsyncMock(return_value=stream_response)
    stream_cm.__aexit__ = AsyncMock(return_value=False)

    client_instance = MagicMock()
    client_instance.stream.return_value = stream_cm

    client_cm = MagicMock()
    client_cm.__aenter__ = AsyncMock(return_value=client_instance)
    client_cm.__aexit__ = AsyncMock(return_value=False)
    mock_async_client.return_value = client_cm

    db_session = MagicMock()
    mock_sessionlocal.return_value = _sessionlocal_cm(db_session)

    chat_request = ChatRequest(
        email="user@example.com",
        query="hi",
        application="webuddhist",
        device_type=DeviceType.web.value,
        thread_id=existing_thread_id,
    )

    async def _collect():
        return [chunk async for chunk in get_chat_stream(chat_request)]

    chunks = asyncio.run(_collect())

    # Should not create a new thread
    mock_create_thread.assert_not_called()
    mock_save_chat.assert_called_once()
    assert any(existing_thread_id.encode("utf-8") in c for c in chunks)


