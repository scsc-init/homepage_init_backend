# 게시글 관련 DB, API 명세서
**최신개정일:** 2025-05-28

# DB 구조

## 게시판 DB
```sql
CREATE TABLE "board" (
	"id"	INTEGER,
	"name"	TEXT,
	"description"	TEXT,
	"writing_permission_level"	INTEGER DEFAULT 0,
	"reading_permission_level"	INTEGER DEFAULT 0,
	PRIMARY KEY("id")
);
```


## 게시글 DB
```sql
CREATE TABLE "article" (
	"id"	INTEGER,
	"title"	TEXT,
	"content"	TEXT,
	"author_id"	TEXT,
	"board_id"	INTEGER,
	"created_at"	DATETIME DEFAULT CURRENT_TIMESTAMP,
	"updated_at"	DATETIME DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("author_id") REFERENCES "user"("id") ON DELETE SET NULL,
	FOREIGN KEY("board_id") REFERENCES "board"("id") ON DELETE CASCADE
)
```


## 댓글 DB
```sql
CREATE TABLE "comment" (
	"id"	INTEGER,
	"content"	TEXT,
	"author_id"	TEXT,
  	"board_id"	INTEGER,
	"post_id"	INTEGER,
	"parent_id"	INTEGER,
	"created_at"	DATETIME DEFAULT CURRENT_TIMESTAMP,
	"updated_at"	DATETIME DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("author_id") REFERENCES "user"("id"),
	FOREIGN KEY("board_id") REFERENCES "board"("id"),
  	FOREIGN KEY("post_id") REFERENCES "article"("id"),
	FOREIGN KEY("parent_id") REFERENCES "comment"("id")
)
```

# API 구조

## 회원 관련 API(/api/user)

- 회원 정보를 관리하는 API
- 회원은 이메일, 이름, 전화번호, 전공 등을 포함하고 있으며, 전공은 `major` 테이블과 외래 키 관계로 연결됨

논의점
- Get All User 기능, Get User by ID 기능을 만들어야 하는지, 만든다면 권한이나 정보 보호는 어떻게 해야 하는지
- Update, Delete User 기능을 admin이 할 수 있게 해야 하는지
- Get My Info에서 정보를 얼마나 가려야 할지

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

수정된 **API 문서**는 아래와 같습니다. 주어진 SQL 정의에 따라 사용자 데이터 형식 (`id`, `phone`, `student_id`, 등)을 반영하여 명확하게 정리했습니다.

---

## 🔹 Get Executives (임원 목록 조회)

- **Method**: `GET`
- **URL**: `/api/user/executives`
- **설명**: 현재 등록된 임원(`executive`) 사용자들의 목록을 조회합니다.
- **Response**:

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

- **Status Codes**:
  - `200 OK`
  - `401 Unauthorized`

---

## 🔹 Get Presidents (회장 목록 조회)

* **Method**: `GET`
* **URL**: `/api/user/presidents`
* **설명**: 현재 등록된 회장(`president`) 사용자들의 목록을 조회합니다.
* **Response**:

```json
[
  {
    "id": "a1b2c3d4e5f67890abcd1234567890ef",
    "email": "president@example.com",
    "name": "이순신",
    "phone": "01098765432",
    "student_id": "202412345",
    "role": "president",
    "status": "active",
    "major_id": 2,
    "last_login": "2025-05-10T08:30:00",
    "created_at": "2024-03-01T00:00:00",
    "updated_at": "2025-02-28T23:59:59"
  }
]
```

- **Status Codes**:
  - `200 OK`
  - `401 Unauthorized`

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

- **Status Codes**:
  - `204 No Content` (기존 유저 로그인)
  - `404 Not Found` (유효하지 않은 email)

> ⚙ `last_login`은 이 시점에서 자동 업데이트.  

---

## 🔹 Logout

- **Method**: `POST`  
- **URL**: `/api/user/logout`  
- **설명**: 로그아웃

- **Status Codes**:
  - `204 No Content` 
  - `401 Unauthorized` (로그인 하지 않음)

---

## 🔹 Change User (관리자 기능)

- **Method**: `POST`  
- **URL**: `/api/executive/user/:id`  
- **설명**: 관리자(executive)가 회원 정보 변경  
- **Request Body**:
```json
{
  "status": "banned"
}
```

- **Status Codes**:
  - `204 No Content`
  - `401 Unauthorized` (로그인하지 않음)
  - `403 Forbidden` (관리자(executive) 권한 없음, 권한 부족)
  - `404 Not Found` (id 사용자 계정 없음)
  - `409 Confilct` (UNIQUE 필드 중복)

---


## 전공 관련 API(/api/major)

- 전공 정보를 관리하는 API
- 전공은 단과대학(college)과 전공 이름(major_name)으로 구성

---

## 🔹 Create Major

- **Method**: `POST`
- **URL**: `/api/executive/major/create`
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
  - `401 Unauthorized` (로그인하지 않음)
  - `403 Forbidden` (관리자(executive) 권한 없음)
  - `409 Conflict` (중복 데이터 삽입)
  - `422 Unprocessable Content`: 필수 필드 누락

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
- **URL**: `/api/major/:id`
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
- **URL**: `/api/executive/major/update/:id`
- **Request Body** (JSON):
```json
{
  "college": "공과대학",
  "major_name": "소프트웨어공학과"
}
```

- **Status Codes**:
  - `204 No Content`: 성공
  - `401 Unauthorized` (로그인하지 않음)
  - `403 Forbidden` (관리자(executive) 권한 없음)
  - `404 Not Found`: 해당 ID 없음
  - `409 Conflict` (중복 데이터 삽입)
  - `422 Unprocessable Content`: 필수 필드 누락

---

## 🔹 Delete Major

- **Method**: `POST`
- **URL**: `/api/executive/major/delete/:id`
- **Response**:

- **Status Codes**:
  - `204 No Content`: 삭제 성공
  - `400 Bad Request`: 외래 키 제약으로 삭제 불가 (`ON DELETE RESTRICT`)
  - `401 Unauthorized` (로그인하지 않음)
  - `403 Forbidden` (관리자(executive) 권한 없음)
  - `404 Not Found`: 해당 ID 없음

---
