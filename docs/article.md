# 게시글 관련 DB, API 명세서
**최신개정일:** 2025-05-28

# DB 구조

## 게시판 DB
```sql
CREATE TABLE "board" (
	"id"	INTEGER,
	"name"	TEXT NOT NULL,
	"description"	TEXT NOT NULL,
	"writing_permission_level"	INTEGER NOT NULL DEFAULT 0,
	"reading_permission_level"	INTEGER NOT NULL DEFAULT 0,
  "created_at"	DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	"updated_at"	DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY("id" AUTOINCREMENT)
);

INSERT INTO board (id, name, description, writing_permission_level, reading_permission_level) VALUES (1, 'sigpig_content', 'sig/pig advertising board', 1000, 0);
```
- sig, pig 홍보글을 저장하는 board를 추가함. 


## 게시글 DB
```sql
CREATE TABLE "article" (
	"id"	INTEGER,
	"title"	TEXT NOT NULL,
	"content"	TEXT NOT NULL,
	"author_id"	TEXT NOT NULL,
	"board_id"	INTEGER NOT NULL,
	"created_at"	DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	"updated_at"	DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("author_id") REFERENCES "user"("id") ON DELETE RESTRICT,
	FOREIGN KEY("board_id") REFERENCES "board"("id") ON DELETE CASCADE
);
```


## 댓글 DB
```sql
CREATE TABLE "comment" (
	"id"	INTEGER,
	"content"	TEXT NOT NULL,
	"author_id"	TEXT NOT NULL,
	"board_id"	INTEGER NOT NULL,
	"post_id"	INTEGER NOT NULL,
	"parent_id"	INTEGER NOT NULL,
	"created_at"	DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	"updated_at"	DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("author_id") REFERENCES "user"("id"),
	FOREIGN KEY("board_id") REFERENCES "board"("id"),
	FOREIGN KEY("post_id") REFERENCES "article"("id"),
	FOREIGN KEY("parent_id") REFERENCES "comment"("id")
);
```

# API 구조

## 게시판 관련 API(/api/board)

- 게시판 정보를 관리하는 API

논의점
- Board 순서를 저장하는 column이 필요할까
- 각 게시판별 관리가 가능한 역할이 따로 있어야 할까
- 게시물을 볼 수 있는 권한과 게시판의 존재를 알 수 있는 권한은 달라야 할까

---

## 🔹 Create Board (게시판 생성)

- **Method**: `POST`  
- **URL**: `/api/executive/board/create`
- **설명**: 게시판 생성
- **Request Body**:
```json
{
  "name": "자유 게시판",
  "description": "누구나 자유롭게 글을 쓸 수 있는 공간입니다.",
  "writing_permission_level": 0,
  "reading_permission_level": 0
}
```
- **Response**:
```json
{
  "id": 1,
  "name": "자유 게시판",
  "description": "누구나 자유롭게 글을 쓸 수 있는 공간입니다.",
  "writing_permission_level": 0,
  "reading_permission_level": 0,
  "created_at": "2025-04-01T12:00:00",
  "updated_at": "2025-04-01T12:00:00"
}
```
- **Status Codes**:
  - `201 Created`
  - `401 Unauthorized`
  - `403 Forbidden` (권한 없음)
  - `409 Conflict` (UNIQUE 필드 중복)
  - `422 Unprocessable Content` (오류, 제약 위반 등)

---

## 🔹 Get Board (게시판 조회)

- **Method**: `GET`  
- **URL**: `/api/board/:id`  
- **설명**: 게시판 정보 조회
- **Response**:
```json
{
  "id": 1,
  "name": "자유 게시판",
  "description": "누구나 자유롭게 글을 쓸 수 있는 공간입니다.",
  "writing_permission_level": 0,
  "reading_permission_level": 0,
  "created_at": "2025-04-01T12:00:00",
  "updated_at": "2025-04-01T12:00:00"
}
```
- **Status Codes**:
  - `200 OK`
  - `401 Unauthorized`
  - `404 Not Found` (게시판이 존재하지 않음)

---

## 🔹 Get Board List (게시판 목록 조회)

- **Method**: `GET`
- **URL**: `/api/boards`
- **설명**: 게시판 목록 조회
- **Response**:

```json
[
  {
  "id": 1,
  "name": "자유 게시판",
  "description": "누구나 자유롭게 글을 쓸 수 있는 공간입니다.",
  "writing_permission_level": 0,
  "reading_permission_level": 0,
  "created_at": "2025-04-01T12:00:00",
  "updated_at": "2025-04-01T12:00:00"
  }
]
```

- **Status Codes**:
  - `200 OK`
  - `401 Unauthorized`

---

## 🔹 Update Board (게시판 정보 수정)

- **Method**: `POST`  
- **URL**: `/api/executive/board/update/:id`  
- **설명**: 게시판 정보 수정  
- **Request Body**:
```json
{
  "name": "자유 게시판",
  "description": "누구나 자유롭게 글을 쓸 수 있는 공간입니다.",
  "writing_permission_level": 0,
  "reading_permission_level": 0
}
```

- **Status Codes**:
  - `204 No Content`
  - `401 Unauthorized`
  - `404 Not Found` (게시판이 존재하지 않음)

---

## 🔹 Delete Board (게시판 삭제)

- **Method**: `POST`  
- **URL**: `/api/executive/board/delete/:id`  
- **설명**: 게시판 삭제  

- **Status Codes**:
  - `204 No Content`
  - `401 Unauthorized`
  - `404 Not Found` (게시판이 존재하지 않음)
  - `409 Conflict` (외래 키 제약으로 인한 삭제 불가)



## 게시글 관련 API(/api/article)

- 게시글을 관리하는 API

---

## 🔹 Create Article (게시글 생성)

- **Method**: `POST`
- **URL**: `/api/article/create`
- **설명**: 게시글 생성
- **Request Body** (JSON):
```json
{
  "title": "안녕하세요",
  "content": "## Hello?",
  "board_id": 1
}
```
- **Response**:
```json
{
  "id": 1,
  "title": "안녕하세요",
  "content": "## Hello?",
  "board_id": 1,
  "author_id": "",
  "created_at": "2025-04-01T12:00:00",
  "updated_at": "2025-04-01T12:00:00"
}
```
- **Status Codes**:
  - `201 Created`
  - `401 Unauthorized` (로그인하지 않음)
  - `403 Forbidden` (권한 없음)
  - `404 Not Found` (게시판이 존재하지 않음)
  - `409 Conflict` (중복 데이터 삽입)
---

## 🔹 Get Article List (게시글 목록 조희)

- **Method**: `GET`
- **URL**: `/api/articles/:board_id`
- **설명**: 게시글 목록 조회, 모든 게시판의 글의 경우 `board_id`=0
- **Response**:
```json
[
  {
    "id": 1,
    "title": "안녕하세요",
    "content": "## Hello?",
    "board_id": 1,
    "author_id": "",
    "created_at": "2025-04-01T12:00:00",
    "updated_at": "2025-04-01T12:00:00"
  }
]
```
- **Status Codes**:
  - `200 OK`
  - `404 Not Found` (게시판이 존재하지 않음)

---

## 🔹 Get Article by ID (ID로 게시글 조회)

- **Method**: `GET`
- **URL**: `/api/article/:id`
- **설명**: 해당 ID의 게시글 조회
- **Response**:
```json
{
  "id": 1,
  "title": "안녕하세요",
  "content": "## Hello?",
  "board_id": 1,
  "author_id": "",
  "created_at": "2025-04-01T12:00:00",
  "updated_at": "2025-04-01T12:00:00"
}
```
- **Status Codes**:
  - `200 OK`
  - `404 Not Found`: 게시글이 존재하지 않음

---

## 🔹 Update Article (게시글 수정)

- **Method**: `POST`
- **URL**: `/api/article/update/:id`
- **설명**: 게시글 수정
- **Request Body** (JSON):
```json
{
  "title": "안녕하세요",
  "content": "## Hello?",
  "board_id": 1
}
```
- **Response**:
```json
{
  "id": 1,
  "title": "안녕하세요",
  "content": "## Hello?",
  "board_id": 1,
  "author_id": "",
  "created_at": "2025-04-01T12:00:00",
  "updated_at": "2025-04-01T12:00:00"
}
```
- **Status Codes**:
  - `204 No Content`
  - `401 Unauthorized` (로그인하지 않음)
  - `403 Forbidden` (게시글의 작성자가 아님)
  - `404 Not Found` (게시판이나 게시글이 존재하지 않음)
  
---

## 🔹 Update Article by Executive (관리자에 의한 게시글 수정)

- **Method**: `POST`
- **URL**: `/api/executive/article/update/:id`
- **설명**: 게시글 수정
- **Request Body** (JSON):
```json
{
  "title": "안녕하세요",
  "content": "## Hello?",
  "board_id": 1
}
```
- **Response**:
```json
{
  "id": 1,
  "title": "안녕하세요",
  "content": "## Hello?",
  "board_id": 1,
  "author_id": "",
  "created_at": "2025-04-01T12:00:00",
  "updated_at": "2025-04-01T12:00:00"
}
```
- **Status Codes**:
  - `204 No Content`
  - `401 Unauthorized` 
  - `403 Forbidden` 
  - `404 Not Found` (게시판이나 게시글이 존재하지 않음)
  
---

## 🔹 Delete Article (작성자에 의한 게시글 삭제)

- **Method**: `POST`
- **URL**: `/api/article/delete/:id`
- **설명**: 작성자에 의한 게시글 삭제

- **Status Codes**:
  - `204 No Content`
  - `401 Unauthorized` (로그인하지 않음)
  - `403 Forbidden` (게시글의 작성자가 아님)
  - `404 Not Found` (게시글이 존재하지 않음)

---

## 🔹 Delete Article by Executive (관리자에 의한 게시글 삭제)

- **Method**: `POST`
- **URL**: `/api/executive/article/delete/:id`
- **설명**: 관리자에 의한 게시글 삭제

- **Status Codes**:
  - `204 No Content`
  - `401 Unauthorized` (로그인하지 않음)
  - `403 Forbidden` (권한 없음)
  - `404 Not Found` (게시글이 존재하지 않음)

---
