from datetime import datetime
from unittest.mock import patch
from uuid import uuid4

from fastapi import status
from fastapi.testclient import TestClient

from chat_api.app import api
from chat_api.applications.applications_response_models import (
    ApplicationCreateRequest,
    ApplicationResponse,
)

client = TestClient(api)


@patch("chat_api.applications.application_views.create_application_service")
def test_create_application_returns_application(mock_create_application_service) -> None:
    expected = ApplicationResponse(
        id=uuid4(),
        name="webuddhist",
        created_at=datetime(2025, 1, 1, 0, 0, 0),
        updated_at=datetime(2025, 1, 1, 0, 0, 0),
    )

    mock_create_application_service.return_value = expected
    resp = client.post("/applications", json={"name": "webuddhist"})

    assert resp.status_code == status.HTTP_200_OK
    mock_create_application_service.assert_called_once()
    assert mock_create_application_service.call_args.kwargs["application"] == ApplicationCreateRequest(
        name="webuddhist"
    )
    assert resp.json() == {
        "id": str(expected.id),
        "name": expected.name,
        "created_at": expected.created_at.isoformat(),
        "updated_at": expected.updated_at.isoformat(),
    }

