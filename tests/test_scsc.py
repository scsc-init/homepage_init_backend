import pytest
from httpx import HTTPStatusError

from tests import factories
from tests.types import DBSessionFactory, SCSCGlobalStatus, SCSCStatus


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
    """SCSC 전역 상태 조회 API가 정상적으로 동작하는지 검증합니다."""
    response = client.get("/api/scsc/global/status", headers=api_headers)
    response.raise_for_status()

    data = response.json()
    assert data["id"] == 1
    assert data["status"] in {"recruiting", "active", "inactive"}


def test_get_global_statuses(client, api_headers):
    """모든 가능한 SCSC 상태를 조회하는 API가 정상적으로 동작하는지 검증합니다."""
    response = client.get("/api/scsc/global/statuses", headers=api_headers)
    response.raise_for_status()

    assert response.json() == {"statuses": ["recruiting", "active", "inactive"]}


def test_update_global_status_success(client, api_headers):
    """정상적인 SCSC 상태 업데이트 시 DB에 저장되고 204 상태 코드를 반환하는지 검증합니다."""
    _set_status(SCSCStatus.inactive)

    response = client.post(
        "/api/executive/scsc/global/status",
        headers=api_headers,
        json={"status": "recruiting"},
    )
    response.raise_for_status()

    assert _get_status().status == SCSCStatus.recruiting


def test_update_global_status_invalid_transition(client, api_headers):
    """유효하지 않은 SCSC 상태 변경 시 400 오류를 발생시키는지 확인합니다."""
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
    """인증되지 않은 사용자가 SCSC 상태 업데이트를 시도할 때 401 오류를 발생시키는지 확인합니다."""
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
    """일반 사용자가 SCSC 상태 업데이트를 시도할 때 403 오류를 발생시키는지 확인합니다."""
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
