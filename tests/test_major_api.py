def test_create_major_success(api_client, build_headers, create_user):
    """임원진이 새 전공을 생성할 수 있는지 확인한다."""
    _, token = create_user(role_level=500)

    payload = {"college": "공과대학", "major_name": "컴퓨터공학부"}
    response = api_client.post(
        "/api/executive/major/create", json=payload, headers=build_headers(token)
    )

    assert response.status_code == 201
    body = response.json()
    assert body["college"] == payload["college"]
    assert body["major_name"] == payload["major_name"]
    assert isinstance(body["id"], int)


def test_create_major_duplicate_returns_409(api_client, build_headers, create_user):
    """이미 존재하는 전공을 다시 만들면 409가 발생하는지 검증한다."""
    _, token = create_user(role_level=500)
    payload = {"college": "공과대학", "major_name": "컴퓨터공학부"}
    first = api_client.post(
        "/api/executive/major/create", json=payload, headers=build_headers(token)
    )
    assert first.status_code == 201

    duplicate = api_client.post(
        "/api/executive/major/create", json=payload, headers=build_headers(token)
    )

    assert duplicate.status_code == 409


def test_get_all_majors_returns_created_entries(
    api_client, build_headers, create_major
):
    """전공 목록 API가 저장된 한글 데이터를 그대로 반환하는지 확인한다."""
    create_major(college="공과대학", major_name="컴퓨터공학부")
    create_major(college="자연과학대학", major_name="수학과")

    response = api_client.get("/api/majors", headers=build_headers())

    assert response.status_code == 200
    majors = response.json()
    assert {m["major_name"] for m in majors} == {"컴퓨터공학부", "수학과"}


def test_get_major_by_id_success(api_client, build_headers, create_major):
    """단일 전공 조회가 정확한 이름을 돌려주는지 검증한다."""
    major = create_major(college="자연과학대학", major_name="화학과")

    response = api_client.get(f"/api/major/{major.id}", headers=build_headers())

    assert response.status_code == 200
    assert response.json()["major_name"] == "화학과"


def test_get_major_by_id_not_found(api_client, build_headers):
    """없는 전공 ID를 조회하면 404가 나는지 확인한다."""
    response = api_client.get("/api/major/999", headers=build_headers())

    assert response.status_code == 404


def test_update_major_success(api_client, build_headers, create_major, create_user):
    """집행 권한 사용자가 전공 이름을 수정할 수 있는지 검증한다."""
    major = create_major(college="공과대학", major_name="토목공학과")
    _, token = create_user(role_level=500)

    response = api_client.post(
        f"/api/executive/major/update/{major.id}",
        json={"college": "공과대학", "major_name": "건설환경공학부"},
        headers=build_headers(token),
    )

    assert response.status_code == 204

    updated = api_client.get(f"/api/major/{major.id}", headers=build_headers())
    assert updated.status_code == 200
    assert updated.json()["major_name"] == "건설환경공학부"


def test_update_major_duplicate_returns_409(
    api_client, build_headers, create_major, create_user
):
    """다른 전공과 동일한 이름으로 수정하면 중복 오류가 발생하는지 확인한다."""
    source = create_major(college="공과대학", major_name="생명공학과")
    target = create_major(college="공과대학", major_name="나노공학과")
    _, token = create_user(role_level=500)

    response = api_client.post(
        f"/api/executive/major/update/{source.id}",
        json={"college": target.college, "major_name": target.major_name},
        headers=build_headers(token),
    )

    assert response.status_code == 409


def test_delete_major_not_found(api_client, build_headers, create_user):
    """삭제 대상 전공이 없을 때 404를 반환하는지 확인한다."""
    _, token = create_user(role_level=500)

    response = api_client.post(
        "/api/executive/major/delete/999",
        headers=build_headers(token),
    )

    assert response.status_code == 404


def test_delete_major_success(api_client, build_headers, create_major, create_user):
    """정상적인 삭제 흐름이 완료되면 재조회 시 404가 되는지 검증한다."""
    target_major = create_major(college="자연과학대학", major_name="지질학과")
    _, token = create_user(role_level=500)

    response = api_client.post(
        f"/api/executive/major/delete/{target_major.id}",
        headers=build_headers(token),
    )

    assert response.status_code == 204

    follow_up = api_client.get(f"/api/major/{target_major.id}", headers=build_headers())
    assert follow_up.status_code == 404
