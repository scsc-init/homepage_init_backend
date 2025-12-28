from src.model import UserStatus


def _create_executive(create_user, issue_jwt_token):
    executive = create_user(role_level=500, status=UserStatus.active)
    return executive, issue_jwt_token(executive.id)


def test_create_major(api_client, build_headers, issue_jwt_token, create_user):
    executive, token = _create_executive(create_user, issue_jwt_token)

    response = api_client.post(
        "/api/executive/major/create",
        json={"college": "테스트대학", "major_name": "테스트학과"},
        headers=build_headers(token),
    )

    assert response.status_code == 201
    assert response.json() == {
        "id": 2,
        "college": "테스트대학",
        "major_name": "테스트학과",
    }


def test_create_existing_major(api_client, build_headers, issue_jwt_token, create_user):
    executive, token = _create_executive(create_user, issue_jwt_token)

    response = api_client.post(
        "/api/executive/major/create",
        json={"college": "테스트대학", "major_name": "테스트학과"},
        headers=build_headers(token),
    )

    assert response.status_code == 201

    response2 = api_client.post(
        "/api/executive/major/create",
        json={"college": "테스트대학", "major_name": "테스트학과"},
        headers=build_headers(token),
    )

    assert response2.status_code == 409
    assert response2.json() == {"detail": "major already exists"}


def test_create_major_with_unprocessable_content(
    api_client, build_headers, issue_jwt_token, create_user
):
    executive, token = _create_executive(create_user, issue_jwt_token)

    response = api_client.post(
        "/api/executive/major/create",
        json={"college": "공과대학"},
        headers=build_headers(token),
    )

    assert response.status_code == 422


def test_create_major_not_logged_in(api_client, build_headers):
    response = api_client.post(
        "/api/executive/major/create",
        json={"college": "테스트대학", "major_name": "테스트학과"},
        headers=build_headers(),
    )
    assert response.status_code == 401


def test_create_major_not_executive(
    api_client, build_headers, issue_jwt_token, create_user, create_major
):
    non_executive_member = create_user(role_level=300)
    token = issue_jwt_token(non_executive_member.id)

    response = api_client.post(
        "/api/executive/major/create",
        json={"college": "테스트대학", "major_name": "테스트학과"},
        headers=build_headers(token),
    )
    assert response.status_code == 403


def get_majors(api_client, build_headers):
    response = api_client.get("/api/majors", headers=build_headers())
    assert response.status_code == 200


def get_majors_by_id(api_client, create_major):
    test_major1 = create_major(college="사회과학대학", major="심리학과")
    test_major2 = create_major(college="공과대학", major="건축학과")
    test_major3 = create_major(college="사범대학", major="영어교육과")
    response1 = api_client.get(f"/api/major/{test_major1.id}")
    response2 = api_client.get(f"/api/major/{test_major2.id}")
    response3 = api_client.get(f"/api/major/{test_major3.id}")

    assert response1.status_code == 200
    assert response1.json() == {
        "id": {test_major1.id},
        "college": "사회과학대학",
        "major_name": "심리학과",
    }

    assert response2.status_code == 200
    assert response2.json() == {
        "id": {test_major2.id},
        "college": "공과대학",
        "major_name": "건축학과",
    }

    assert response3.status_code == 200
    assert response3.json() == {
        "id": {test_major3.id},
        "college": "사범대학",
        "major_name": "영어교육과",
    }


def test_update_major(
    api_client, build_headers, issue_jwt_token, create_user, create_major
):
    executive, token = _create_executive(create_user, issue_jwt_token)
    test_major = create_major(college="테스트대학", major_name="테스트")

    response = api_client.post(
        f"/api/executive/major/update/{test_major.id}",
        json={"college": "테스트대학", "major_name": "테스트학과"},
        headers=build_headers(token),
    )
    assert response.status_code == 204


def test_update_existing_major(
    api_client, build_headers, issue_jwt_token, create_user, create_major
):
    executive, token = _create_executive(create_user, issue_jwt_token)
    first_major = create_major(college="인문대학", major_name="영어영문학과")
    second_major = create_major(college="인문대학", major_name="국어국문학과")

    response = api_client.post(
        f"/api/executive/major/update/{first_major.id}",
        json={"college": "인문대학", "major_name": "국어국문학과"},
        headers=build_headers(token),
    )
    assert response.status_code == 409
    assert response.json() == {"detail": "major already exists"}


def test_update_nonexisting_major(
    api_client, build_headers, issue_jwt_token, create_user
):
    executive, token = _create_executive(create_user, issue_jwt_token)

    response = api_client.post(
        "/api/executive/major/update/1000",
        json={"college": "테스트대학", "major_name": "테스트학과"},
        headers=build_headers(token),
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "major not found"}


def test_update_major_with_unprocessable_content(
    api_client, build_headers, issue_jwt_token, create_user, create_major
):
    executive, token = _create_executive(create_user, issue_jwt_token)
    test_major = create_major(college="자연과학대학", major_name="지구환경과학부")

    response = api_client.post(
        "/api/executive/major/update/:1",
        json={"college": "자연과학대학"},
        headers=build_headers(token),
    )
    assert response.status_code == 422


def test_update_major_not_logged_in(
    api_client, build_headers, issue_jwt_token, create_user, create_major
):
    test_major = create_major(college="테스트대학", major_name="테스트")

    response = api_client.post(
        f"/api/executive/major/update/{test_major.id}",
        json={"college": "테스트대학", "major_name": "테스트학과"},
        headers=build_headers(),
    )
    assert response.status_code == 401


def test_update_major_not_executive(
    api_client, build_headers, issue_jwt_token, create_user, create_major
):
    test_user = create_user(role_level=300)
    token = issue_jwt_token(test_user.id)
    test_major = create_major(college="테스트대학", major_name="테스트")

    response = api_client.post(
        f"/api/executive/major/update/{test_major.id}",
        json={"college": "테스트대학", "major_name": "테스트학과"},
        headers=build_headers(token),
    )
    assert response.status_code == 403


def test_delete_major(
    api_client, build_headers, issue_jwt_token, create_user, create_major
):
    executive, token = _create_executive(create_user, issue_jwt_token)
    test_major = create_major(college="테스트대학", major_name="테스트학과")

    response = api_client.post(
        f"/api/executive/major/delete/{test_major.id}",
        headers=build_headers(token),
    )

    assert response.status_code == 204


def test_delete_major_bad_request(
    api_client, build_headers, issue_jwt_token, create_user, create_major
):
    executive, token = _create_executive(create_user, issue_jwt_token)
    test_major = create_major(college="사회과학대학", major_name="사회학과")
    referenced_user = create_user(role_level=300, major=test_major)

    response = api_client.post(
        f"/api/executive/major/delete/{test_major.id}",
        headers=build_headers(token),
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Cannot delete major: it is referenced by existing users"
    }


def test_delete_major_not_logged_in(api_client, build_headers, create_major):
    test_major = create_major(college="인문대학", major_name="언어학과")

    response = api_client.post(
        f"/api/executive/major/delete/{test_major.id}",
        headers=build_headers(),
    )
    assert response.status_code == 401


def test_delete_major_not_executive(
    api_client, build_headers, issue_jwt_token, create_user, create_major
):
    non_executive_member = create_user(role_level=300)
    token = issue_jwt_token(non_executive_member.id)
    test_major = create_major(college="공과대학", major_name="전기정보공학부")

    response = api_client.post(
        f"/api/executive/major/delete/{test_major.id}",
        headers=build_headers(token),
    )
    assert response.status_code == 403


def test_delete_nonexisting_major(
    api_client, build_headers, issue_jwt_token, create_user
):
    executive, token = _create_executive(create_user, issue_jwt_token)

    response = api_client.post(
        "/api/executive/major/delete/1000",
        headers=build_headers(token),
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "major not found"}
