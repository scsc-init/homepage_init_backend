from tests.types import HTTPMethod, UserStatus


def test_api_secret_required_for_public_request(api_client):
    """공개 전공 목록을 시크릿 없이 조회하면 거절되는지 검증한다."""
    response = api_client.get("/api/majors")

    assert response.status_code == 401


def test_invalid_api_secret_is_rejected(api_client):
    """잘못된 시크릿 값으로 요청하면 인증 실패가 발생하는지 확인한다."""
    response = api_client.get("/api/majors", headers={"x-api-secret": "not-valid"})

    assert response.status_code == 401


def test_executive_routes_require_authentication(api_client, build_headers):
    """임원 전용 API를 인증 없이 호출할 수 없는지 확인한다."""
    response = api_client.post(
        "/api/executive/major/create",
        json={"college": "Engineering", "major_name": "Computer Science"},
        headers=build_headers(),
    )

    assert response.status_code == 401


def test_user_status_rule_blocks_matching_status(
    api_client, build_headers, create_status_rule, create_user
):
    """차단 대상 상태의 사용자가 접근하면 규칙에 의해 거절되는지 검증한다."""
    create_status_rule(
        user_status=UserStatus.standby, method=HTTPMethod.GET, path="/api/majors"
    )
    _, token = create_user(status=UserStatus.standby)

    response = api_client.get("/api/majors", headers=build_headers(token))

    assert response.status_code == 403


def test_user_status_rule_allows_other_statuses(
    api_client, build_headers, create_status_rule, create_user
):
    """허용된 상태의 사용자는 정상적으로 목록을 열람할 수 있는지 확인한다."""
    create_status_rule(
        user_status=UserStatus.standby, method=HTTPMethod.GET, path="/api/majors"
    )
    _, token = create_user(status=UserStatus.active)

    response = api_client.get("/api/majors", headers=build_headers(token))

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
