# 졸업생 관련 DB, API 명세서
**최신개정일:** 2025-06-18

# DB 구조

## Oldboy DB
```sql
CREATE TABLE oldboy_applicant (
    id TEXT PRIMARY KEY,
    processed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id) REFERENCES user(id) ON DELETE CASCADE
);
```

### SQL 관련
```sql
CREATE TRIGGER update_oldboy_applicant_updated_at
AFTER UPDATE ON oldboy_applicant
FOR EACH ROW
WHEN 
    OLD.processed != NEW.processed
BEGIN
    UPDATE oldboy_applicant
    SET updated_at = CURRENT_TIMESTAMP
    WHERE id = OLD.id;
END;

CREATE INDEX idx_oldboy_applicant_processed ON oldboy_applicant(processed);
```

# API 구조

## 졸업 신청자 관리 API (`/api/oldboy`)

- `oldboy_applicant` 테이블의 데이터를 관리하는 API입니다.
- 이 테이블은 `user` 테이블의 `id`를 참조하며, 졸업 신청자의 처리 여부와 신청/업데이트 시각을 기록합니다.

---

## 🔹 Register Oldboy Applicant

- **Method**: `POST`
- **URL**: `/api/oldboy/register`
- **Description**: 로그인된 사용자에 대해 새로운 졸업 신청자 기록을 생성합니다. 가입한 지 3년이 지난 정회원이 신청할 수 있습니다. 

- **Response**:
```json
{
  "id": "user_id_from_user_table",
  "processed": false,
  "created_at": "2023-10-27T10:00:00Z",
  "updated_at": "2023-10-27T10:00:00Z"
}
```
- **Status Codes**:
  - `201 Created`: 생성 성공
  - `400 Bad Request`: oldboy 신청 자격 없음
  - `401 Unauthorized` (로그인하지 않음)
  - `409 Conflict`: 이미 존재하는 `id`로 신청을 시도

---

## 🔹 Get All Oldboy Applicants

- **Method**: `GET`
- **URL**: `/api/executive/oldboy/applicants`
- **Description**: 졸업 신청자 기록을 조회합니다.
- **Query Parameters**:
    - `processed`: Allowed values: `true`, `false`
- **Response**:
```json
[
  {
    "id": "user123",
    "processed": false,
    "created_at": "2023-10-27T10:00:00Z",
    "updated_at": "2023-10-27T10:00:00Z"
  },
  {
    "id": "user456",
    "processed": false,
    "created_at": "2023-10-26T09:00:00Z",
    "updated_at": "2023-10-27T11:30:00Z"
  }
]
```
- **Status Codes**:
  - `200 OK`: 조회 성공 (데이터가 없으면 빈 배열 반환)
  - `401 Unauthorized` (로그인하지 않음)
  - `403 Forbidden` (관리자(executive) 권한 없음)

---

## 🔹 Process Oldboy Applicant

- **Method**: `POST`
- **URL**: `/api/executive/oldboy/:id/process`
- **Description**: 특정 졸업 신청자의 `processed` 상태를 업데이트하고 졸업 신청자의 권한을 `oldboy`로 변경합니다. 
- **Status Codes**:
  - `204 No Content`: 업데이트 성공 (응답 본문 없음)
  - `401 Unauthorized`: 로그인하지 않음
  - `403 Forbidden`: 권한 없음 (예: 관리자가 아님)
  - `404 Not Found`: 해당 ID의 졸업 신청 기록 없음

---

## 🔹 Unregister Oldboy Applicant(Self)

- **Method**: `POST`
- **URL**: `/api/oldboy/unregister`
- **Description**: 로그인한 사용자의 졸업 신청자 기록이 처리되지 않았다면 삭제합니다. 
- **Status Codes**:
  - `204 No Content`: 삭제 성공
  - `400 Bad Request`: 이미 oldboy로 처리됨
  - `401 Unauthorized`: 로그인하지 않음
  - `404 Not Found`: 해당 ID의 졸업 신청 기록 없음

---

## 🔹 Unregister Oldboy Applicant(Executive)

- **Method**: `POST`
- **URL**: `/api/executive/oldboy/:id/unregister`
- **Description**: 특정 `id`를 가진 졸업 신청자 기록을 삭제합니다. 
- **Status Codes**:
  - `204 No Content`: 삭제 성공
  - `401 Unauthorized`: 로그인하지 않음
  - `403 Forbidden`: 권한 없음 (예: 관리자가 아님)
  - `404 Not Found`: 해당 ID의 졸업 신청 기록 없음

---

## 🔹 Reactivate Oldboy Applicant(Self)

- **Method**: `POST`
- **URL**: `/api/oldboy/reactivate`
- **Description**: 로그인한 사용자의 권한이 oldboy이면 권한을 member로 바꾸고 상태를 pending으로 바꾼다. 
- **Status Codes**:
  - `204 No Content`
  - `400 Bad Request`: oldboy가 아님
  - `401 Unauthorized`: 로그인하지 않음

---
