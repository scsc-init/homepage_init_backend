# 회원 관련 DB, API 명세서
**최신개정일:** 2025-05-02

# DB 구조

## 회원 DB
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    phone TEXT NOT NULL UNIQUE,
    student_id TEXT NOT NULL UNIQUE,
    role TEXT DEFAULT 'user' NOT NULL CHECK (role IN ('user', 'executive', 'president')),
    status TEXT DEFAULT 'pending' NOT NULL CHECK (status IN ('active', 'pending', 'banned')),

    major_id INTEGER NOT NULL,
    FOREIGN KEY (major_id) REFERENCES majors(id) ON DELETE RESTRICT

    last_login DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
);
```
- 2025-04-29 spec을 SQLite 형식으로 수정함(By GPT)
- VARCHAR -> TEXT, ENUM -> CHECK
- 모든 column을 NOT NULL로 변경
- ON UPDATE는 없어서 TRIGGER로 처리
- PK인 id에 관해서는 추후 논의
- phone, student_id를 정수로 처리하는게 나을지 논의. 문자열이면 형식을 어떻게 할지 정해야 함.
```sql
CREATE TRIGGER update_users_updated_at
AFTER UPDATE ON users
FOR EACH ROW
WHEN 
    OLD.email IS NOT NEW.email OR
    OLD.name IS NOT NEW.name OR
    OLD.phone IS NOT NEW.phone OR
    OLD.student_id IS NOT NEW.student_id OR
    OLD.role IS NOT NEW.role OR
    OLD.status IS NOT NEW.status OR
    OLD.major_id IS NOT NEW.major OR
BEGIN
    UPDATE users
    SET updated_at = CURRENT_TIMESTAMP
    WHERE id = OLD.id;
END;
```

## 전공 DB
필요성
- 전공에 대한 유효성 검사를 하드코딩으로 하는 것은 별로일듯
- 첨단융합학부(2024년 신설), 농업생명과학대학 스마트시스템과학과(2025년 신설)처럼 새로운 전공이 생김

논의점
- 다전공을 처리해야 하는지
- 학부, 대학원 모두 서울대이면 대학원 기준으로 할지

```sql
CREATE TABLE majors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    college TEXT NOT NULL,
    major_name TEXT,
    UNIQUE (college, major_name)
);
```

나중에 까먹을까봐 적어둠:
- 외래 키 기본 비활성화: 앱에서 PRAGMA foreign_keys = ON; 실행 필요

# API 구조

## 회원 관련 API(/api/users)

- 회원 정보를 관리하는 API
- 회원은 이메일, 이름, 전화번호, 전공 등을 포함하고 있으며, 전공은 `majors` 테이블과 외래 키 관계로 연결됨

논의점
- Get All Users 기능, Get User by ID 기능을 만들어야 하는지, 만든다면 권한이나 정보 보호는 어떻게 해야 하는지
- Update, Delete User 기능을 admin이 할 수 있게 해야 하는지
- 로그인 유지 방식을 어떻게 처리할지: `from starlette.middleware.sessions import SessionMiddleware`을 사용할까?
- Get My Info에서 정보를 얼마나 가려야 할지

---

## 🔹 Create User (회원 등록)

- **Method**: `POST`  
- **URL**: `/api/users/create`
- **설명**: 회원 최초 등록. 
- **Request Body**:
```json
{
  "frontend_secret": "some-secret-code",
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
  "id": 1,
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
  - `400 Bad Request` (오류, 제약 위반 등)
  - `401 Unauthorized` (인증 실패 시)
  - `409 Conflict` (UNIQUE 필드 중복)

---

## 🔹 Get My Info (내 정보 조회)

- **Method**: `GET`  
- **URL**: `/api/users/profile`  
- **설명**: 로그인한 사용자의 정보 조회
- **Response**:
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "홍길동",
  "phone": "010-1234-5678",
  "student_id": "20230123",
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

## 🔹 Update My Info (내 정보 수정)

- **Method**: `POST`  
- **URL**: `/api/users/update`  
- **설명**: 로그인한 사용자의 정보 수정  
- **Request Body**:
```json
{
  "name": "김철수",
  "phone": "010-5678-1234", 
  "student_id": "20231234", 
  "major_id": 2
}
```
- **Response**:
```json
{
  "updated": true
}
```
- **Status Codes**:
  - `200 OK`
  - `400 Bad Request`
  - `401 Unauthorized`
  - `409 Conflict` (UNIQUE 필드 중복)

---

## 🔹 Delete My Account (회원 탈퇴)

- **Method**: `POST`  
- **URL**: `/api/users/delete`  
- **설명**: 로그인한 사용자의 계정을 삭제함  
- **Response**:
```json
{
  "deleted": true
}
```
- **Status Codes**:
  - `200 OK`
  - `401 Unauthorized`
  - `403 Forbidden` (관리자 계정은 자기 삭제 불가 등)

---

## 🔹 Login

- **Method**: `POST`  
- **URL**: `/api/users/login`  
- **설명**: 로그인
- **Request Body**:
```json
{
  "frontend_secret": "some-secret-code",
  "email": "user@example.com",
}
```
- **Response**:
```json
null
```
- **Status Codes**:
  - `200 OK` (기존 유저 로그인)
  - `401 Unauthorized` (유효하지 않은 이메일 정보)

> ⚙ `last_login`은 이 시점에서 자동 업데이트.  

---

## 🔹 Change User (관리자 기능)

- **Method**: `POST`  
- **URL**: `/api/executive/users/:id`  
- **설명**: 관리자(executive)가 회원 정보 변경  
- **Request Body**:
```json
{
  "status": "banned"
}
```
- **Response**:
```json
{
  "updated": true
}
```
- **Status Codes**:
  - `200 OK`
  - `400 Bad Request` (유효하지 않은 상태값)
  - `401 Unauthorized` (로그인하지 않음)
  - `403 Forbidden` (관리자(executive) 권한 없음)
  - `404 Not Found`

---


## 전공 관련 API(/api/majors)

- 전공 정보를 관리하는 API
- 전공은 단과대학(college)과 전공 이름(major_name)으로 구성

---

## 🔹 Create Major

- **Method**: `POST`
- **URL**: `/api/executive/majors`
- **Request Body** (JSON):
```json
{
  "college": "공과대학",
  "major_name": "컴퓨터공학과"
}
```
- **Response**:
```json
{
  "id": 1,
  "college": "공과대학",
  "major_name": "컴퓨터공학과"
}
```
- **Status Codes**:
  - `201 Created`: 생성 성공
  - `400 Bad Request`: 필수 필드 누락 또는 중복
  - `401 Unauthorized` (로그인하지 않음)
  - `403 Forbidden` (관리자(executive) 권한 없음)

---

## 🔹 Get All Majors

- **Method**: `GET`
- **URL**: `/api/majors`
- **Response**:
```json
[
  {
    "id": 1,
    "college": "공과대학",
    "major_name": "컴퓨터공학과"
  },
  {
    "id": 2,
    "college": "문과대학",
    "major_name": "철학과"
  }
]
```
- **Status Codes**:
  - `200 OK`

---

## 🔹 Get Major by ID

- **Method**: `GET`
- **URL**: `/api/majors/:id`
- **Response**:
```json
{
  "id": 1,
  "college": "공과대학",
  "major_name": "컴퓨터공학과"
}
```
- **Status Codes**:
  - `200 OK`
  - `404 Not Found`: 해당 ID의 전공 없음

---

## 🔹 Update Major

- **Method**: `POST`
- **URL**: `/api/executive/majors/update/:id`
- **Request Body** (JSON):
```json
{
  "college": "공과대학",
  "major_name": "소프트웨어공학과"
}
```
- **Response**:
```json
{
  "updated": true
}
```
- **Status Codes**:
  - `200 OK`: 성공
  - `400 Bad Request`: 필드 누락 또는 유효성 오류
  - `401 Unauthorized` (로그인하지 않음)
  - `403 Forbidden` (관리자(executive) 권한 없음)
  - `404 Not Found`: 해당 ID 없음

---

## 🔹 Delete Major

- **Method**: `POST`
- **URL**: `/api/executive/majors/delete/:id`
- **Response**:
```json
{
  "deleted": true
}
```
- **Status Codes**:
  - `200 OK`: 삭제 성공
  - `400 Bad Request`: 외래 키 제약으로 삭제 불가 (`ON DELETE RESTRICT`)
  - `401 Unauthorized` (로그인하지 않음)
  - `403 Forbidden` (관리자(executive) 권한 없음)
  - `404 Not Found`: 해당 ID 없음

---
