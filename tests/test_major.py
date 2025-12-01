# tests/test_major.py

from fastapi.testclient import TestClient

from .main import app

client = TestClient(app)


def test_create_major():
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

    res = client.post(
        "/api/executive/major/create",
        json={"college": "테스트대학", "major_name": "테스트학과"},
    )
    assert res.status_code == 201
    assert res.json() == {"id": 1, "college": "테스트대학", "major_name": "테스트학과"}


def test_create_existing_major():
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

    res = client.post(
        "/api/executive/major/create",
        json={"college": "공과대학", "major_name": "컴퓨터공학과"},
    )
    assert res.status_code == 409
    assert res.json() == {"detail": "major already exists"}


def test_create_major_with_unprocessable_content():
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

    res = client.post(
        "/api/executive/major/create",
        json={"college": "공과대학"},
    )
    assert res.status_code == 422


def test_create_major_not_logged_in():
    res = client.post(
        "/api/executive/major/create",
        json={"college": "테스트대학", "major_name": "테스트학과"},
    )
    assert res.status_code == 401


def test_create_major_not_executive():
    login_res = client.post(
        "/api/user/login",
        json={
            "email": "member@example.com",
            "hashToken": "b6e346dee08f8e8cf029179eb5177b5c2fc1a6e8ba01ab8ff4e1b8d56e89298c",
        },
    )
    assert login_res.status_code == 200
    login_data = login_res.json()
    jwt = login_data.get("jwt")
    assert jwt, f"JWT가 응답에 없습니다. 응답: {login_data}"

    res = client.post(
        "/api/executive/major/create",
        json={"college": "테스트대학", "major_name": "테스트학과"},
    )
    assert res.status_code == 403


def get_majors():
    res = client.get("/api/majors")
    assert res.status_code == 200


def get_majors_by_id():
    res1 = client.get("/api/major/:1")
    res10 = client.get("/api/major/:10")
    res20 = client.get("/api/major/:20")
    res30 = client.get("/api/major/:30")
    res40 = client.get("/api/major/:40")
    res50 = client.get("/api/major/:50")
    res60 = client.get("/api/major/:60")

    assert res1.status_code == 200
    assert res1.json() == {"id": 1, "college": "공과대학", "major_name": "컴퓨터공학과"}

    assert res10.status_code == 200
    assert res10.json() == {
        "id": 10,
        "college": "인문대학",
        "major_name": "아시아언어문명학부",
    }

    assert res20.status_code == 200
    assert res20.json() == {
        "id": 20,
        "college": "사회과학대학",
        "major_name": "심리학과",
    }

    assert res30.status_code == 200
    assert res30.json() == {"id": 30, "college": "간호대학", "major_name": "간호대학"}

    assert res40.status_code == 200
    assert res40.json() == {"id": 40, "college": "공과대학", "major_name": "산업공학과"}

    assert res50.status_code == 200
    assert res50.json() == {
        "id": 50,
        "college": "농업생명과학대학",
        "major_name": "조경·지역시스템공학부",
    }

    assert res60.status_code == 200
    assert res60.json() == {"id": 60, "college": "사범대학", "major_name": "영어교육과"}


def test_update_major():
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

    res = client.post(
        "/api/executive/major/update/:1",
        json={"college": "테스트대학", "major_name": "테스트학과"},
    )
    assert res.status_code == 204


def test_update_existing_major():
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

    res = client.post(
        "/api/executive/major/update/:1",
        json={"college": "공과대학", "major_name": "컴퓨터공학과"},
    )
    assert res.status_code == 409
    assert res.json() == {"detail": "major already exists"}


def test_update_nonexisting_major():
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

    res = client.post(
        "/api/executive/major/update/:1",
        json={"college": "테스트대학", "major_name": "테스트학과"},
    )
    assert res.status_code == 404
    assert res.json() == {"detail": "major not found"}


def test_update_major_with_unprocessable_content():
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

    res = client.post(
        "/api/executive/major/update/:1",
        json={"college": "테스트대학"},
    )
    assert res.status_code == 422


def test_update_major_not_logged_in():
    res = client.post(
        "/api/executive/major/update/:1",
        json={"college": "테스트대학", "major_name": "테스트학과"},
    )
    assert res.status_code == 401


def test_update_major_not_executive():
    login_res = client.post(
        "/api/user/login",
        json={
            "email": "member@example.com",
            "hashToken": "b6e346dee08f8e8cf029179eb5177b5c2fc1a6e8ba01ab8ff4e1b8d56e89298c",
        },
    )
    assert login_res.status_code == 200
    login_data = login_res.json()
    jwt = login_data.get("jwt")
    assert jwt, f"JWT가 응답에 없습니다. 응답: {login_data}"

    res = client.post(
        "/api/executive/major/update/:1",
        json={"college": "테스트대학", "major_name": "테스트학과"},
    )
    assert res.status_code == 403


def test_delete_major():
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

    res = client.post(
        "/api/executive/major/delete/:1",
    )

    assert res.status_code == 204


def test_delete_major_bad_request():
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

    res = client.post(
        "/api/executive/major/delete/:1",
    )

    assert res.status_code == 400
    assert res.json() == {
        "detail": "Cannot delete major: it is referenced by existing users"
    }


def test_delete_major_not_logged_in():
    res = client.post(
        "/api/executive/major/delete/:1",
    )
    assert res.status_code == 401


def test_delete_major_not_executive():
    login_res = client.post(
        "/api/user/login",
        json={
            "email": "member@example.com",
            "hashToken": "b6e346dee08f8e8cf029179eb5177b5c2fc1a6e8ba01ab8ff4e1b8d56e89298c",
        },
    )
    assert login_res.status_code == 200
    login_data = login_res.json()
    jwt = login_data.get("jwt")
    assert jwt, f"JWT가 응답에 없습니다. 응답: {login_data}"

    res = client.post(
        "/api/executive/major/delete/:1",
    )
    assert res.status_code == 403


def test_delete_nonexisting_major():
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

    res = client.post(
        "/api/executive/major/delete/:100",
    )
    assert res.status_code == 404
    assert res.json() == {"detail": "major not found"}
