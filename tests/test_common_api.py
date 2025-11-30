from src.model import HTTPMethod, UserStatus


def test_api_secret_required_for_public_request(api_client):
    response = api_client.get("/api/majors")

    assert response.status_code == 401
    assert response.json()["detail"] == "No x-api-secret included"


def test_invalid_api_secret_is_rejected(api_client):
    response = api_client.get("/api/majors", headers={"x-api-secret": "not-valid"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid x-api-secret"


def test_executive_routes_require_authentication(api_client, build_headers):
    response = api_client.post(
        "/api/executive/major/create",
        json={"college": "Engineering", "major_name": "Computer Science"},
        headers=build_headers(),
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_user_status_rule_blocks_matching_status(
    api_client, build_headers, issue_jwt_token, create_status_rule, create_user
):
    create_status_rule(
        user_status=UserStatus.standby, method=HTTPMethod.GET, path="/api/majors"
    )
    standby_user = create_user(status=UserStatus.standby)
    token = issue_jwt_token(standby_user.id)

    response = api_client.get("/api/majors", headers=build_headers(token))

    assert response.status_code == 403
    assert "cannot access" in response.json()["detail"]


def test_user_status_rule_allows_other_statuses(
    api_client, build_headers, issue_jwt_token, create_status_rule, create_user
):
    create_status_rule(
        user_status=UserStatus.standby, method=HTTPMethod.GET, path="/api/majors"
    )
    active_user = create_user(status=UserStatus.active)
    token = issue_jwt_token(active_user.id)

    response = api_client.get("/api/majors", headers=build_headers(token))

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
