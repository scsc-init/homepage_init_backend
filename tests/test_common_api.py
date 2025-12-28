from src.model import UserStatus
from src.util import generate_user_hash, sha256_hash


def test_user_login_success(
    api_client, create_user, issue_jwt_token, build_headers, db_session
):
    test_user = create_user(role_level=300, status=UserStatus.active)
    test_user.email = "test@example.com"
    test_user.id = sha256_hash(test_user.email.lower())
    token = issue_jwt_token(test_user.id)
    hash_token = generate_user_hash("test@example.com")
    db_session.commit()

    login_res = api_client.post(
        "/api/user/login",
        json={
            "email": "test@example.com",
            "hashToken": hash_token,
        },
        headers=build_headers(token),
    )
    assert login_res.status_code == 200
    login_data = login_res.json()
    jwt = login_data.get("jwt")

    assert jwt, f"JWT가 응답에 없습니다. 응답: {login_data}"


def test_user_login_not_found(
    api_client, create_user, issue_jwt_token, build_headers, db_session
):
    test_user = create_user(role_level=300, status=UserStatus.active)
    test_user.email = "test@example.com"
    test_user.id = sha256_hash(test_user.email.lower())
    token = issue_jwt_token(test_user.id)
    hash_token = generate_user_hash("test@example.com")

    login_res = api_client.post(
        "/api/user/login",
        json={
            "email": "test@example.com",
            "hashToken": hash_token,
        },
        headers=build_headers(token),
    )
    assert login_res.status_code == 404
    login_data = login_res.json()
    detail = login_data.get("detail")

    assert detail, "invalid email address"


def test_user_login_wrong_token(
    api_client, create_user, issue_jwt_token, build_headers, db_session
):
    test_user = create_user(role_level=300, status=UserStatus.active)
    test_user.email = "test@example.com"
    test_user.id = sha256_hash(test_user.email.lower())
    token = issue_jwt_token(test_user.id)
    db_session.commit()

    login_res = api_client.post(
        "/api/user/login",
        json={
            "email": "test@example.com",
            "hashToken": "wrong_token",
        },
        headers=build_headers(token),
    )
    assert login_res.status_code == 401
    login_data = login_res.json()
    detail = login_data.get("detail")

    assert detail, "invalid hash token"
