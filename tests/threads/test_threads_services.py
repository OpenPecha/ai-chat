from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException, status

from chat_api.threads.models import DeviceType
from chat_api.threads.threads_request_model import ThreadCreateRequest
from chat_api.threads.threads_services import create_thread


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


