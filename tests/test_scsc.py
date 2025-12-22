import pytest
from httpx import HTTPStatusError

from src.db import DBSessionFactory
from src.model import SCSCGlobalStatus, SCSCStatus
from tests import factories


def _set_status(status: SCSCStatus):
    session = DBSessionFactory().make_session()
    try:
        factories.create_scsc_global_status(session, status=status)
    finally:
        session.close()


def _get_status() -> SCSCGlobalStatus:
    session = DBSessionFactory().make_session()
    try:
        return session.get(SCSCGlobalStatus, 1)
    finally:
        session.close()


def test_get_global_status(client, api_headers):
    response = client.get("/api/scsc/global/status", headers=api_headers)
    response.raise_for_status()

    data = response.json()
    assert data["id"] == 1
    assert data["status"] in {"recruiting", "active", "inactive"}


def test_get_global_statuses(client, api_headers):
    response = client.get("/api/scsc/global/statuses", headers=api_headers)
    response.raise_for_status()

    assert response.json() == {"statuses": ["recruiting", "active", "inactive"]}


def test_update_global_status_success(client, api_headers):
    _set_status(SCSCStatus.inactive)

    response = client.post(
        "/api/executive/scsc/global/status",
        headers=api_headers,
        json={"status": "recruiting"},
    )
    response.raise_for_status()

    assert _get_status().status == SCSCStatus.recruiting


def test_update_global_status_invalid_transition(client, api_headers):
    _set_status(SCSCStatus.inactive)

    response = client.post(
        "/api/executive/scsc/global/status",
        headers=api_headers,
        json={"status": "active"},
    )

    with pytest.raises(HTTPStatusError):
        response.raise_for_status()
    assert _get_status().status == SCSCStatus.inactive


def test_update_global_status_requires_auth(client, api_headers, set_current_user):
    _set_status(SCSCStatus.inactive)
    set_current_user(None)

    response = client.post(
        "/api/executive/scsc/global/status",
        headers=api_headers,
        json={"status": "recruiting"},
    )

    with pytest.raises(HTTPStatusError):
        response.raise_for_status()
    assert _get_status().status == SCSCStatus.inactive


def test_update_global_status_requires_executive(client, api_headers, set_current_user):
    session = DBSessionFactory().make_session()
    try:
        member = factories.create_user(
            session,
            role_level=factories.DEFAULT_ROLE_LEVELS["member"],
        )
    finally:
        session.close()

    set_current_user(member)
    _set_status(SCSCStatus.inactive)

    response = client.post(
        "/api/executive/scsc/global/status",
        headers=api_headers,
        json={"status": "recruiting"},
    )

    with pytest.raises(HTTPStatusError):
        response.raise_for_status()
    assert _get_status().status == SCSCStatus.inactive
