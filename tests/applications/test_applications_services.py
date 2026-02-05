from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException, status

from chat_api.applications.applications_response_models import ApplicationCreateRequest
from chat_api.applications.applications_services import (
    create_application_service,
    get_application_by_name_service,
)


def _sessionlocal_cm(session):
    cm = MagicMock()
    cm.__enter__.return_value = session
    cm.__exit__.return_value = False
    return cm


@patch("chat_api.applications.applications_services.get_application_by_name")
@patch("chat_api.applications.applications_services.SessionLocal")
def test_get_application_by_name_service_success(mock_sessionlocal, mock_get_by_name) -> None:
    db_session = MagicMock()
    mock_sessionlocal.return_value = _sessionlocal_cm(db_session)

    fake_application = MagicMock()
    mock_get_by_name.return_value = fake_application

    result = get_application_by_name_service(db=MagicMock(), name="webuddhist")

    assert result is fake_application
    mock_sessionlocal.assert_called_once()
    mock_get_by_name.assert_called_once_with(db_session, name="webuddhist")


@patch("chat_api.applications.applications_services.get_application_by_name")
@patch("chat_api.applications.applications_services.SessionLocal")
def test_get_application_by_name_service_not_found(mock_sessionlocal, mock_get_by_name) -> None:
    db_session = MagicMock()
    mock_sessionlocal.return_value = _sessionlocal_cm(db_session)
    mock_get_by_name.return_value = None

    with pytest.raises(HTTPException) as exc:
        get_application_by_name_service(db=MagicMock(), name="missing")

    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc.value.detail == "Application not found"


@patch("chat_api.applications.applications_services.create_application_repo")
@patch("chat_api.applications.applications_services.SessionLocal")
def test_create_application_service_success(mock_sessionlocal, mock_create_repo) -> None:
    db_session = MagicMock()
    mock_sessionlocal.return_value = _sessionlocal_cm(db_session)

    req = ApplicationCreateRequest(name="webuddhist")
    fake_created = MagicMock()
    mock_create_repo.return_value = fake_created

    result = create_application_service(application=req)

    assert result is fake_created
    mock_sessionlocal.assert_called_once()
    mock_create_repo.assert_called_once_with(db_session, application=req)


