from src.util import generate_user_hash


def test_create_external_member_application(api_client, build_headers):
    email = "external-applicant@example.com"

    response = api_client.post(
        "/api/user/external/register",
        headers=build_headers(),
        json={
            "email": email,
            "name": "외부회원 신청자",
            "phone": "01012345678",
            "student_id": None,
            "reason": "외부회원 가입 신청",
            "hashToken": generate_user_hash(email),
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["email"] == email
    assert data["name"] == "외부회원 신청자"
    assert data["status"] == "pending"


def test_approve_external_member_application(
    api_client,
    build_headers,
    create_user,
    db_session,
):
    from src.model import User
    from src.util import sha256_hash

    email = "approved-external@example.com"

    create_response = api_client.post(
        "/api/user/external/register",
        headers=build_headers(),
        json={
            "email": email,
            "name": "승인 대상 외부회원",
            "phone": "01087654321",
            "student_id": None,
            "reason": "승인 테스트",
            "hashToken": generate_user_hash(email),
        },
    )
    assert create_response.status_code == 201

    application_id = create_response.json()["id"]
    _, executive_token = create_user(role_level=500)

    approve_response = api_client.post(
        f"/api/executive/user/external/{application_id}/approve",
        headers=build_headers(executive_token),
    )

    assert approve_response.status_code == 200
    assert approve_response.json()["status"] == "approved"

    external_user = db_session.get(User, sha256_hash(email))
    assert external_user is not None
    assert external_user.role == 350
    assert external_user.is_active is True
    assert external_user.student_id is None
    assert external_user.major_id is None


def test_reject_external_member_application(
    api_client,
    build_headers,
    create_user,
):
    email = "rejected-external@example.com"

    create_response = api_client.post(
        "/api/user/external/register",
        headers=build_headers(),
        json={
            "email": email,
            "name": "거절 대상 외부회원",
            "phone": "01011112222",
            "student_id": None,
            "reason": "거절 테스트",
            "hashToken": generate_user_hash(email),
        },
    )
    assert create_response.status_code == 201

    application_id = create_response.json()["id"]
    _, executive_token = create_user(role_level=500)

    reject_response = api_client.post(
        f"/api/executive/user/external/{application_id}/reject",
        headers=build_headers(executive_token),
    )

    assert reject_response.status_code == 200
    assert reject_response.json()["status"] == "rejected"


def test_duplicate_external_member_application_is_rejected(
    api_client,
    build_headers,
):
    email = "duplicate-external@example.com"
    payload = {
        "email": email,
        "name": "중복 신청자",
        "phone": "01033334444",
        "student_id": None,
        "reason": "중복 신청 테스트",
        "hashToken": generate_user_hash(email),
    }

    first_response = api_client.post(
        "/api/user/external/register",
        headers=build_headers(),
        json=payload,
    )
    second_response = api_client.post(
        "/api/user/external/register",
        headers=build_headers(),
        json=payload,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_non_executive_cannot_approve_external_member_application(
    api_client,
    build_headers,
    create_user,
):
    email = "unauthorized-approval@example.com"

    create_response = api_client.post(
        "/api/user/external/register",
        headers=build_headers(),
        json={
            "email": email,
            "name": "권한 테스트 신청자",
            "phone": "01055556666",
            "student_id": None,
            "reason": "권한 테스트",
            "hashToken": generate_user_hash(email),
        },
    )
    assert create_response.status_code == 201

    application_id = create_response.json()["id"]
    _, member_token = create_user(role_level=300)

    approve_response = api_client.post(
        f"/api/executive/user/external/{application_id}/approve",
        headers=build_headers(member_token),
    )

    assert approve_response.status_code == 403


def test_non_executive_cannot_get_external_member_applications(
    api_client,
    build_headers,
    create_user,
):
    _, member_token = create_user(role_level=300)

    response = api_client.get(
        "/api/executive/user/external/applicants",
        headers=build_headers(member_token),
    )

    assert response.status_code == 403


def test_rejected_external_member_can_reapply(
    api_client,
    build_headers,
    create_user,
):
    email = "reapply-external@example.com"
    initial_payload = {
        "email": email,
        "name": "최초 신청자",
        "phone": "01011112222",
        "student_id": None,
        "reason": "최초 신청",
        "hashToken": generate_user_hash(email),
    }

    create_response = api_client.post(
        "/api/user/external/register",
        headers=build_headers(),
        json=initial_payload,
    )
    assert create_response.status_code == 201

    application_id = create_response.json()["id"]
    _, executive_token = create_user(role_level=500)

    reject_response = api_client.post(
        f"/api/executive/user/external/{application_id}/reject",
        headers=build_headers(executive_token),
    )
    assert reject_response.status_code == 200
    assert reject_response.json()["status"] == "rejected"

    reapply_response = api_client.post(
        "/api/user/external/register",
        headers=build_headers(),
        json={
            **initial_payload,
            "name": "재신청자",
            "phone": "01099998888",
            "reason": "내용을 수정하여 재신청",
        },
    )

    assert reapply_response.status_code == 201

    data = reapply_response.json()
    assert data["id"] == application_id
    assert data["name"] == "재신청자"
    assert data["phone"] == "01099998888"
    assert data["reason"] == "내용을 수정하여 재신청"
    assert data["status"] == "pending"
    assert data["reviewed_by"] is None


def test_external_member_kakao_name_is_stored_and_propagated_on_approval(
    api_client,
    build_headers,
    create_user,
    db_session,
):
    from src.model import User
    from src.util import sha256_hash

    email = "kakao-external@example.com"

    create_response = api_client.post(
        "/api/user/external/register",
        headers=build_headers(),
        json={
            "email": email,
            "name": "카톡 이름 신청자",
            "phone": "01033334444",
            "student_id": None,
            "reason": "카톡 이름 테스트",
            "kakao_name": "실제카톡이름",
            "hashToken": generate_user_hash(email),
        },
    )
    assert create_response.status_code == 201
    assert create_response.json()["kakao_name"] == "실제카톡이름"

    application_id = create_response.json()["id"]
    _, executive_token = create_user(role_level=500)

    approve_response = api_client.post(
        f"/api/executive/user/external/{application_id}/approve",
        headers=build_headers(executive_token),
    )
    assert approve_response.status_code == 200

    external_user = db_session.get(User, sha256_hash(email))
    assert external_user is not None
    assert external_user.kakao_name == "실제카톡이름"
