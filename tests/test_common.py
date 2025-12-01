# tests/test_common.py

from fastapi.testclient import TestClient

from .main import app

client = TestClient(app)


def test_user_login():
    login_res = client.post(
        "/api/user/login",
        json={
            "email": "exec@example.com",
            "hashToken": "12350b93cae7322f29d409e12a998a598c703780c5f00c99ddf372c38817e4f4",
        },
    )
    assert login_res.status_code == 200
    login_data = login_res.json()
    jwt = login_data.get("jwt")

    assert jwt, f"JWT가 응답에 없습니다. 응답: {login_data}"
