# 회원 관련 DB, API 명세서
**최신개정일:** 2025-06-18

# DB 구조

## 회원 DB
```sql
CREATE TABLE user (
    id TEXT PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    phone TEXT NOT NULL UNIQUE,
    student_id TEXT NOT NULL UNIQUE,
    role INTEGER NOT NULL,
    status TEXT DEFAULT 'pending' NOT NULL CHECK (status IN ('active', 'pending', 'banned')),

    last_login DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    major_id INTEGER NOT NULL,
    FOREIGN KEY (major_id) REFERENCES major(id) ON DELETE RESTRICT,
    FOREIGN KEY (role) REFERENCES user_role(level) ON DELETE RESTRICT
);
```
- id는 email의 hash 사용. hash는 sha256을 사용. 
- phone은 `01012345678`처럼 대시 없는 숫자 문자열 형식. (`/^010\d{8}$/`)
- student_id는 `202512345`처럼 대시 없는 숫자 문자열 형식. (`/^(\d{4})\d{5}$/`, group 1 should be valid year)

### SQL 관련
```sql
CREATE TRIGGER update_user_updated_at
AFTER UPDATE ON user
FOR EACH ROW
WHEN 
    OLD.email != NEW.email OR
    OLD.name != NEW.name OR
    OLD.phone != NEW.phone OR
    OLD.student_id != NEW.student_id OR
    OLD.role != NEW.role OR
    OLD.status != NEW.status OR
    OLD.major_id != NEW.major_id
BEGIN
    UPDATE user
    SET updated_at = CURRENT_TIMESTAMP
    WHERE id = OLD.id;
END;

CREATE INDEX idx_user_major ON user(major_id);
CREATE INDEX idx_user_role ON user(role);
```


# API 구조

## 회원 관련 API(/api/user)

- 회원 정보를 관리하는 API
- 회원은 이메일, 이름, 전화번호, 전공 등을 포함하고 있으며, 전공은 `major` 테이블과 외래 키 관계로 연결됨

---

## 🔹 Create User (회원 등록)

- **Method**: `POST`  
- **URL**: `/api/user/create`
- **설명**: 회원 최초 등록. 
- **Request Body**:
```json
{
  "email": "user@example.com",
  "name": "홍길동",
  "phone": "01012345678",
  "student_id": "202312345",
  "major_id": 1
}
```
- **Response**:
```json
{
  "id": "b4c9a289323b21a01c3e940f150eb9b8c542587f1abfd8f0e1cc1ffc5e475514",
  "email": "user@example.com",
  "name": "홍길동",
  "phone": "01012345678",
  "student_id": "202312345",
  "role": "user",
  "status": "pending",
  "major_id": 1,
  "last_login": "2025-04-01T12:00:00",
  "created_at": "2025-04-01T12:00:00",
  "updated_at": "2025-04-01T12:00:00"
}
```
- **Status Codes**:
  - `201 Created`
  - `401 Unauthorized` (인증 실패 시)
  - `409 Conflict` (UNIQUE 필드 중복)
  - `422 Unprocessable Content` (오류, 제약 위반 등)

---

## 🔹 Enroll User (사용자 등록)

* **Method**: `POST`
* **URL**: `/api/user/enroll`
* **설명**: `pending` 상태의 사용자를 `active` 상태로 등록(활성화)합니다. 이 엔드포인트는 로그인된 사용자의 현재 상태를 변경하는 데 사용됩니다.
* **Status Codes**:
  * `204 No Content`: 사용자가 성공적으로 `active` 상태로 등록되었습니다.
  * `400 Bad Request`: 현재 로그인된 사용자의 상태가 `pending`이 아닌 경우
  * `401 Unauthorized`: 로그인하지 않았거나 유효한 인증 정보가 없습니다.
  * `404 Not Found`: (이 경우는 내부적으로 발생할 가능성이 매우 낮지만, 만약 `current_user.id`에 해당하는 사용자를 데이터베이스에서 찾을 수 없을 때 반환될 수 있습니다.)

---

## 🔹 Get My Profile (내 정보 조회)

- **Method**: `GET`  
- **URL**: `/api/user/profile`  
- **설명**: 로그인한 사용자의 정보 조회
- **Response**:
```json
{
  "id": "b4c9a289323b21a01c3e940f150eb9b8c542587f1abfd8f0e1cc1ffc5e475514",
  "email": "user@example.com",
  "name": "홍길동",
  "phone": "01012345678",
  "student_id": "202312345",
  "role": "user",
  "status": "active",
  "major_id": 1,
  "last_login": "2025-05-01T09:00:00",
  "created_at": "2025-04-01T12:00:00",
  "updated_at": "2025-04-30T12:00:00"
}
```
- **Status Codes**:
  - `200 OK`
  - `401 Unauthorized` (인증 실패 시)

---

## 🔹 Get User by ID

- **Method**: `GET`  
- **URL**: `/api/user/:id`  
- **설명**: ID로 사용자의 정보(이메일, 이름, 학과) 조회
- **Response**:
```json
{
  "id": "b4c9a289323b21a01c3e940f150eb9b8c542587f1abfd8f0e1cc1ffc5e475514",
  "email": "user@example.com",
  "name": "홍길동",
  "major_id": 1,
}
```
- **Status Codes**:
  - `200 OK`
  - `401 Unauthorized` (인증 실패 시)
  - `404 Not Found` (유효하지 않은 ID)

---

## 🔹 Get Users by Role (임원 목록 조회)

* **Method**: `GET`
* **URL**: `/api/users`
* **Description**: 임원 이상의 권한에 대해 해당 권한의 사용자를 조회한다. 
* **Query Parameters**:
    * `user_role`: (Required) Specifies the role of the users to retrieve.
        * Allowed values: `executive`, `president`
* **Example Request**:
    * To get executives: `/api/users?user_role=executive`
    * To get presidents: `/api/users?user_role=president`
* **Response**:

```json
[
  {
    "id": "f81d4fae7dec11d0a76500a0c91e6bf6",
    "email": "executive@example.com",
    "name": "홍길동",
    "phone": "01012345678",
    "student_id": "202512345",
    "role": "executive",
    "status": "active",
    "major_id": 1,
    "last_login": "2025-05-01T09:00:00",
    "created_at": "2025-04-01T12:00:00",
    "updated_at": "2025-04-30T12:00:00"
  }
]
```

* **Status Codes**:
    * `200 OK`
    * `400 Bad Request`: If the `role` query parameter is invalid.
    * `401 Unauthorized`

---

## 🔹 Update My Profile (내 정보 수정)

- **Method**: `POST`  
- **URL**: `/api/user/update`  
- **설명**: 로그인한 사용자의 정보 수정  
- **Request Body**:
```json
{
  "name": "김철수",
  "phone": "01056781234", 
  "student_id": "202312345", 
  "major_id": 2
}
```

- **Status Codes**:
  - `204 No Content`
  - `401 Unauthorized`
  - `409 Conflict` (UNIQUE 필드 중복)
  - `422 Unprocessable Content`

---

## 🔹 Delete My Profile (회원 탈퇴)

- **Method**: `POST`  
- **URL**: `/api/user/delete`  
- **설명**: 로그인한 사용자의 계정을 삭제함  

- **Status Codes**:
  - `204 No Content`
  - `401 Unauthorized`
  - `403 Forbidden` (관리자 계정은 자기 삭제 불가 등)
  - `409 Conflict` : 외래 키 제약으로 인한 삭제 불가

---

## 🔹 Login

- **Method**: `POST`  
- **URL**: `/api/user/login`  
- **설명**: 로그인
- **Request Body**:
```json
{
  "email": "user@example.com"
}
```

- **Request Body**:
```json
{
  "jwt":"some-encoded-jwt"
}
```

- **Status Codes**:
  - `200 OK` (기존 유저 로그인)
  - `404 Not Found` (유효하지 않은 email)

> ⚙ `last_login`은 이 시점에서 자동 업데이트.  

---

## 🔹 Change User (관리자 기능)

- **Method**: `POST`  
- **URL**: `/api/executive/user/:id`  
- **설명**: 관리자(`executive`)가 특정 회원의 정보를 변경합니다.
- **Path Parameters**:
    - `id` (string, required): 변경할 사용자 계정의 고유 ID.
- **Request Body**:
    * 모든 필드는 선택 사항입니다. 제공된 필드만 업데이트됩니다.
    * `status` 필드의 가능한 값은 `active`, `pending`, `banned` 등 User 테이블 정의에서 `status`의 check 부분에 있는 값입니다. 

```json
{
  "name": "새로운 이름",
  "phone": "01099998888",
  "student_id": "202654321",
  "major_id": 3,
  "role": "executive",
  "status": "active"
}
```

- **Status Codes**:
  - `204 No Content`: 사용자 정보가 성공적으로 변경되었습니다.
  - `401 Unauthorized`: 로그인하지 않았거나 유효한 인증 정보가 없습니다.
  - `403 Forbidden`:
      - 관리자(`executive`) 권한이 없거나,
      - 자신보다 높거나 같은 등급의 역할을 가진 사용자의 정보를 변경하려는 경우,
      - 자신보다 높은 등급의 역할을 사용자에게 부여하려는 경우.
  - `404 Not Found`: 제공된 `id`에 해당하는 사용자 계정을 찾을 수 없습니다.
  - `409 Conflict`: `phone` 또는 `student_id`와 같은 UNIQUE 필드 값이 이미 존재합니다.
  - `422 Unprocessable Entity`:
      - `phone` 번호 형식이 유효하지 않은 경우.
      - `student_id` 형식이 유효하지 않은 경우.

---

