# 테스트 관련 API 명세서

**최신개정일:** 2026-01-28

# API 구조

* **보안 사항**: 서버 설정에서 `enable_test_routes`가 `true`여야 작동합니다.

## 테스트 유저 관련 API (/api/test/users)

* 테스트 목적의 유저 데이터를 생성, 조회, 삭제하기 위한 API입니다.

---

## Create Test User

* **Method**: `POST`
* **URL**: `/api/test/users`
* **Request Body** (JSON):

```json
{
  "email": "user@example.com",
  "name": "홍길동",
  "phone": "010-1234-5678",
  "student_id": "2024-12345",
  "major_id": 1,
  "role_name": "executive",
  "status": "active",
  "profile_picture": "https://example.com/photo.jpg",
  "profile_picture_is_url": true,
  "discord_id": 123456789,
  "discord_name": "gildong#1234"
}

```

* **Response**:

```json
{
  "id": "hash of email",
  "email": "user@example.com",
  "name": "홍길동",
  "phone": "010-1234-5678",
  "student_id": "2024-12345",
  "role": 500,
  "major_id": 1,
  "status": "active",
  "discord_id": 123456789,
  "discord_name": "gildong#1234",
  "profile_picture": "https://example.com/photo.jpg",
  "profile_picture_is_url": true,
  "last_login": "2026-01-28T15:30:00",
  "created_at": "2026-01-28T15:30:00",
  "updated_at": "2026-01-28T15:30:00"
}

```

* **Status Codes**:
* `201 Created`: 생성 성공
* `401 Unauthorized`: API 시크릿 인증 실패
* `404 Not Found`: 존재하지 않는 `major_id` 입력
* `409 Conflict`: 중복된 이메일, 학번, 또는 전화번호
* `422 Unprocessable Content`:
  * 전화번호/학번 형식 오류
  * `profile_picture_is_url`이 true이나 사진 경로가 누락된 경우



---

## List Test Users

* **Method**: `GET`
* **URL**: `/api/test/users`
* **Query Parameters**:
* `email` (Optional): 이메일 필터링
* `name` (Optional): 이름 필터링


* **Response**: `Array of UserResponse` (위에 정의된 구조의 배열)
* **Status Codes**:
  * `200 OK`


---

## Delete Test User

* **Method**: `DELETE`
* **URL**: `/api/test/users/:user_id`
* **Description**: 유저 삭제 시 관련 데이터(`StandbyReq`, `OldboyApplicant`)도 함께 삭제를 시도합니다.
* **Status Codes**:
  * `204 No Content`: 삭제 성공
  * `404 Not Found`: 해당 ID의 유저 없음
  * `409 Conflict`: 외래 키 제약 조건으로 인해 삭제 불가



---

## Delete All Test Users

* **Method**: `DELETE`
* **URL**: `/api/test/users`
* **Description**: 모든 테스트 유저 및 관련 레코드를 일괄 삭제합니다.
* **Status Codes**:
  * `204 No Content`: 전체 삭제 성공
  * `409 Conflict`: 참조 무결성 오류 발생



---
