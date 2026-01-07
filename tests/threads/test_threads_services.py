from unittest.mock import MagicMock, patch
from uuid import uuid4
from datetime import datetime

import pytest
from fastapi import HTTPException, status

from chat_api.threads.models import DeviceType
from chat_api.threads.threads_request_model import ThreadCreateRequest
from chat_api.threads.threads_services import create_thread
from chat_api.threads.thread_service import ThreadService
from chat_api.threads.thread_repository import ThreadRepository


def _sessionlocal_cm(session):
    cm = MagicMock()
    cm.__enter__.return_value = session
    cm.__exit__.return_value = False
    return cm


@patch("chat_api.threads.threads_services.create_thread_repo")
@patch("chat_api.threads.threads_services.get_application_by_name_service")
@patch("chat_api.threads.threads_services.SessionLocal")
def test_create_thread_success(
    mock_sessionlocal, mock_get_application_by_name_service, mock_create_thread_repo
) -> None:
    db_session = MagicMock()
    mock_sessionlocal.return_value = _sessionlocal_cm(db_session)

    req = ThreadCreateRequest(
        email="user@example.com",
        device_type=DeviceType.web,
        application_name="webuddhist",
    )

    fake_application = MagicMock()
    fake_application.id = MagicMock()
    mock_get_application_by_name_service.return_value = fake_application

    fake_thread = MagicMock()
    mock_create_thread_repo.return_value = fake_thread

    result = create_thread(thread_request=req)

    assert result is fake_thread
    mock_sessionlocal.assert_called_once()
    mock_get_application_by_name_service.assert_called_once_with(
        db_session, name="webuddhist"
    )
    mock_create_thread_repo.assert_called_once_with(
        db_session, application_id=fake_application.id, thread_request=req
    )


@patch("chat_api.threads.threads_services.create_thread_repo")
@patch("chat_api.threads.threads_services.get_application_by_name_service")
@patch("chat_api.threads.threads_services.SessionLocal")
def test_create_thread_application_not_found(
    mock_sessionlocal, mock_get_application_by_name_service, mock_create_thread_repo
) -> None:
    db_session = MagicMock()
    mock_sessionlocal.return_value = _sessionlocal_cm(db_session)

    req = ThreadCreateRequest(
        email="user@example.com",
        device_type=DeviceType.web,
        application_name="missing",
    )
    mock_get_application_by_name_service.return_value = None

    with pytest.raises(HTTPException) as exc:
        create_thread(thread_request=req)

    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc.value.detail == "Application not found"
    mock_create_thread_repo.assert_not_called()


def test_transform_chats_to_messages_with_new_format() -> None:
    """Test transform_chats_to_messages with new list-based response format."""
    mock_repository = MagicMock(spec=ThreadRepository)
    service = ThreadService(mock_repository)
    
    chat_id = uuid4()
    mock_chat = MagicMock()
    mock_chat.id = chat_id
    mock_chat.question = "what is emptiness"
    mock_chat.created_at = datetime.utcnow()
    mock_chat.response = [
        {
            "type": "search_results",
            "data": [
                {
                    "id": "xcdDbp2XjCM3c8CwSuHqk",
                    "title": "དབུ་མ་ལ་འཇུག་པའི་འགྲེལ་བཤད་ཅེས་བྱ་བ།",
                    "text": "གང་ཟག་གི་བདག་མེད་པ་ནི་བདག་གི་རང་བཞིན་མེད་པ་ཉིད་ཡིན་ལ།"
                },
                {
                    "id": "oXFc8EKNlB02bo8JMtuBU",
                    "title": "བྱང་ཆུབ་སེམས་དཔའི་སྤྱོད་པ་ལ་འཇུག་པའི་ཟིན་བྲིས།",
                    "text": "དོན་ལ་རང་བཞིན་གྱིས་གྲུབ་པའི་གང་ཟག་གི་བདག་གཅིག་མེད་པར་ངེས་སོ། །"
                }
            ]
        },
        {
            "type": "token",
            "data": "Emptiness refers to the lack of inherent existence."
        },
        {
            "type": "done",
            "data": {}
        }
    ]
    
    messages = service.transform_chats_to_messages([mock_chat])
    
    assert len(messages) == 2  # user message + assistant message
    
    # Check user message
    assert messages[0].role == "user"
    assert messages[0].content == "what is emptiness"
    assert messages[0].id == chat_id
    assert messages[0].searchResults is None
    
    # Check assistant message
    assert messages[1].role == "assistant"
    assert messages[1].content == "Emptiness refers to the lack of inherent existence."
    assert messages[1].id == chat_id
    assert messages[1].searchResults is not None
    assert len(messages[1].searchResults) == 2
    assert messages[1].searchResults[0].id == "xcdDbp2XjCM3c8CwSuHqk"
    assert messages[1].searchResults[0].title == "དབུ་མ་ལ་འཇུག་པའི་འགྲེལ་བཤད་ཅེས་བྱ་བ།"
    assert messages[1].searchResults[1].id == "oXFc8EKNlB02bo8JMtuBU"


def test_transform_chats_to_messages_with_old_format() -> None:
    """Test transform_chats_to_messages with old dict-based response format for backward compatibility."""
    mock_repository = MagicMock(spec=ThreadRepository)
    service = ThreadService(mock_repository)
    
    chat_id = uuid4()
    mock_chat = MagicMock()
    mock_chat.id = chat_id
    mock_chat.question = "test question"
    mock_chat.created_at = datetime.utcnow()
    mock_chat.response = {
        "answer": "test answer",
        "search_results": [
            {
                "id": "123",
                "title": "Test Title",
                "text": "Test text"
            }
        ]
    }
    
    messages = service.transform_chats_to_messages([mock_chat])
    
    assert len(messages) == 2
    assert messages[1].content == "test answer"
    assert messages[1].searchResults is not None
    assert len(messages[1].searchResults) == 1
    assert messages[1].searchResults[0].id == "123"


def test_transform_chats_to_messages_no_search_results() -> None:
    """Test transform_chats_to_messages when there are no search results."""
    mock_repository = MagicMock(spec=ThreadRepository)
    service = ThreadService(mock_repository)
    
    chat_id = uuid4()
    mock_chat = MagicMock()
    mock_chat.id = chat_id
    mock_chat.question = "simple question"
    mock_chat.created_at = datetime.utcnow()
    mock_chat.response = [
        {
            "type": "token",
            "data": "Simple answer"
        },
        {
            "type": "done",
            "data": {}
        }
    ]
    
    messages = service.transform_chats_to_messages([mock_chat])
    
    assert len(messages) == 2
    assert messages[1].content == "Simple answer"
    assert messages[1].searchResults is None


