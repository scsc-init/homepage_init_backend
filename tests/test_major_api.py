from src.model import UserStatus


def _create_executive(create_user, issue_jwt_token):
    executive = create_user(role_level=500, status=UserStatus.active)
    return executive, issue_jwt_token(executive.id)


def test_create_major_success(api_client, build_headers, issue_jwt_token, create_user):
    executive, token = _create_executive(create_user, issue_jwt_token)

    payload = {"college": "Engineering", "major_name": "Computer Science"}
    response = api_client.post(
        "/api/executive/major/create", json=payload, headers=build_headers(token)
    )

    assert response.status_code == 201
    body = response.json()
    assert body["college"] == payload["college"]
    assert body["major_name"] == payload["major_name"]
    assert isinstance(body["id"], int)


def test_create_major_duplicate_returns_409(
    api_client, build_headers, create_user, issue_jwt_token
):
    _, token = _create_executive(create_user, issue_jwt_token)
    payload = {"college": "Engineering", "major_name": "Computer Science"}
    first = api_client.post(
        "/api/executive/major/create", json=payload, headers=build_headers(token)
    )
    assert first.status_code == 201

    duplicate = api_client.post(
        "/api/executive/major/create", json=payload, headers=build_headers(token)
    )

    assert duplicate.status_code == 409
    assert duplicate.json()["detail"] == "major already exists"


def test_get_all_majors_returns_created_entries(
    api_client, build_headers, create_major
):
    create_major(college="Engineering", major_name="Computer Science")
    create_major(college="Science", major_name="Mathematics")

    response = api_client.get("/api/majors", headers=build_headers())

    assert response.status_code == 200
    majors = response.json()
    assert {m["major_name"] for m in majors} == {"Computer Science", "Mathematics"}


def test_get_major_by_id_success(api_client, build_headers, create_major):
    major = create_major(college="Science", major_name="Chemistry")

    response = api_client.get(f"/api/major/{major.id}", headers=build_headers())

    assert response.status_code == 200
    assert response.json()["major_name"] == "Chemistry"


def test_get_major_by_id_not_found(api_client, build_headers):
    response = api_client.get("/api/major/999", headers=build_headers())

    assert response.status_code == 404
    assert response.json()["detail"] == "major not found"


def test_update_major_requires_executive_role(
    api_client, build_headers, issue_jwt_token, create_user, create_major
):
    major = create_major(college="Engineering", major_name="Aerospace")
    member = create_user(role_level=300)
    token = issue_jwt_token(member.id)

    response = api_client.post(
        f"/api/executive/major/update/{major.id}",
        json={"college": "Engineering", "major_name": "Astronautics"},
        headers=build_headers(token),
    )

    assert response.status_code == 403
    assert (
        response.json()["detail"]
        == "Permission denied: at least executive role required"
    )


def test_update_major_success(
    api_client, build_headers, create_user, issue_jwt_token, create_major
):
    major = create_major(college="Engineering", major_name="Civil")
    _, token = _create_executive(create_user, issue_jwt_token)

    response = api_client.post(
        f"/api/executive/major/update/{major.id}",
        json={"college": "Engineering", "major_name": "Civil and Environmental"},
        headers=build_headers(token),
    )

    assert response.status_code == 204

    updated = api_client.get(f"/api/major/{major.id}", headers=build_headers())
    assert updated.status_code == 200
    assert updated.json()["major_name"] == "Civil and Environmental"


def test_update_major_duplicate_returns_409(
    api_client, build_headers, create_user, issue_jwt_token, create_major
):
    source = create_major(college="Engineering", major_name="Bio")
    target = create_major(college="Engineering", major_name="Nano")
    _, token = _create_executive(create_user, issue_jwt_token)

    response = api_client.post(
        f"/api/executive/major/update/{source.id}",
        json={"college": target.college, "major_name": target.major_name},
        headers=build_headers(token),
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "major already exists"


def test_delete_major_blocked_by_foreign_key(
    api_client, build_headers, create_user, issue_jwt_token, create_major
):
    target_major = create_major(college="Science", major_name="Biology")
    create_user(role_level=300, major=target_major)
    _, token = _create_executive(create_user, issue_jwt_token)

    response = api_client.post(
        f"/api/executive/major/delete/{target_major.id}",
        headers=build_headers(token),
    )

    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "Cannot delete major: it is referenced by existing users"
    )


def test_delete_major_not_found(
    api_client, build_headers, create_user, issue_jwt_token
):
    _, token = _create_executive(create_user, issue_jwt_token)

    response = api_client.post(
        "/api/executive/major/delete/999",
        headers=build_headers(token),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "major not found"


def test_delete_major_success(
    api_client, build_headers, create_user, issue_jwt_token, create_major
):
    target_major = create_major(college="Science", major_name="Geology")
    _, token = _create_executive(create_user, issue_jwt_token)

    response = api_client.post(
        f"/api/executive/major/delete/{target_major.id}",
        headers=build_headers(token),
    )

    assert response.status_code == 204

    follow_up = api_client.get(f"/api/major/{target_major.id}", headers=build_headers())
    assert follow_up.status_code == 404
