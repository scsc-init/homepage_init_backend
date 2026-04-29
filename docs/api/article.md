# 게시글 관련 DB, API 명세서
**최신개정일:** 2026-04-10

# DB 구조

## 게시판 DB
```sql
CREATE TABLE "board" (
  "id" INTEGER,
  "name" TEXT NOT NULL,
  "description" TEXT NOT NULL,
  "writing_permission_level" INTEGER NOT NULL DEFAULT 0,
  "reading_permission_level" INTEGER NOT NULL DEFAULT 0,
  "created_at" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updated_at" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY("id" AUTOINCREMENT),
  FOREIGN KEY (writing_permission_level) REFERENCES user_role(level) ON DELETE RESTRICT,
  FOREIGN KEY (reading_permission_level) REFERENCES user_role(level) ON DELETE RESTRICT
);
```

## 게시글 DB
```sql
CREATE TABLE "article" (
  "id" INTEGER,
  "title" TEXT NOT NULL,
  "author_id" TEXT NOT NULL,
  "board_id" INTEGER NOT NULL,
  "content" TEXT,
  "created_at" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updated_at" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY("id" AUTOINCREMENT),
  FOREIGN KEY("author_id") REFERENCES "user"("id") ON DELETE RESTRICT,
  FOREIGN KEY("board_id") REFERENCES "board"("id") ON DELETE CASCADE
);
```
```sql
CREATE INDEX idx_board_id ON article(board_id);
```
- article의 content는 `ARTICLE_DIR(static/article/)`에 md 파일로 저장된다. 

2026-04-28 migration:
```sql
DELETE FROM article
WHERE is_deleted = true
  AND id NOT IN (
    SELECT content_id FROM sig
    UNION
    SELECT content_id FROM pig
  );
ALTER TABLE article DROP COLUMN is_deleted;
ALTER TABLE article DROP COLUMN deleted_at;
```

## 첨부파일 DB
```sql
CREATE TABLE attachment (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  article_id INTEGER NOT NULL,
  file_id TEXT NOT NULL,
  UNIQUE (article_id, file_id),
  FOREIGN KEY (article_id) REFERENCES article(id) ON DELETE CASCADE,
  FOREIGN KEY (file_id) REFERENCES file_metadata(id) ON DELETE CASCADE
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

## Create Board (게시판 생성)

- **Method**: `POST`  
- **URL**: `/api/executive/board/create`
- **설명**: 게시판 생성
- **Request Body**:
```json
{
  "name": "자유 게시판",
  "description": "누구나 자유롭게 글을 쓸 수 있는 공간입니다.",
  "writing_permission_level": 0,
  "reading_permission_level": 0,
  "board_type": "TEXT"
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
  "board_type": "TEXT",
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

## Get Board (게시판 조회)

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
  "board_type": "TEXT",
  "created_at": "2025-04-01T12:00:00",
  "updated_at": "2025-04-01T12:00:00"
}
```
- **Status Codes**:
  - `200 OK`
  - `401 Unauthorized`
  - `404 Not Found` (게시판이 존재하지 않음)

---

## Get Board List (게시판 목록 조회)

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
  "board_type": "TEXT",
  "created_at": "2025-04-01T12:00:00",
  "updated_at": "2025-04-01T12:00:00"
  }
]
```

- **Status Codes**:
  - `200 OK`
  - `401 Unauthorized`

---

## Update Board (게시판 정보 수정)

- **Method**: `POST`  
- **URL**: `/api/executive/board/update/:id`  
- **설명**: 게시판 정보 수정  
- **Request Body**:
```json
{
  "name": "자유 게시판",
  "description": "누구나 자유롭게 글을 쓸 수 있는 공간입니다.",
  "writing_permission_level": 0,
  "reading_permission_level": 0,
  "board_type": "TEXT",
}
```

- **Status Codes**:
  - `204 No Content`
  - `401 Unauthorized`
  - `404 Not Found` (게시판이 존재하지 않음)

---

## Delete Board (게시판 삭제)

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

## Create Article (게시글 생성)

- **Method**: `POST`
- **URL**: `/api/article/create`
- **설명**: 게시글 생성
- **Request Body** (JSON):
  - attachments: optional; 없으면 빈 리스트로 처리된다. 중복되거나 존재하지 않는 파일 ID는 무시되며, 응답 시에는 Attachment 객체 리스트로 반환된다.
```json
{
  "title": "안녕하세요",
  "content": "## Hello?",
  "board_id": 1,
  "attachments": ["file_id_1", "file_id_2"]
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
  "updated_at": "2025-04-01T12:00:00",
  "attachments": [
    {
      "id": 1,
      "article_id": 1,
      "file_id": "file_id"
    }
  ]
}
```
- **Status Codes**:
  - `201 Created`
  - `401 Unauthorized` (로그인하지 않음)
  - `403 Forbidden` (권한 없음)
  - `404 Not Found` (게시판이 존재하지 않음)
  - `409 Conflict` (중복 데이터 삽입)
  
---

## Get Articles List (게시글 목록 조희)

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

## Get Article by ID (ID로 게시글 조회)

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
  "updated_at": "2025-04-01T12:00:00",
  "attachments": [
    {
      "id": 1,
      "article_id": 1,
      "file_id": "file_id"
    }
  ]
}
```
- **Status Codes**:
  - `200 OK`
  - `404 Not Found`: 게시글이 존재하지 않음

---

## Update Article (게시글 수정)

- **Method**: `POST`
- **URL**: `/api/article/update/:id`
- **설명**: 게시글 수정
- **Request Body** (JSON):
  - attachments: optional; 없으면 빈 리스트로 처리된다. **수정 성공 시 응답은 업데이트된 Attachment 객체 리스트를 반환한다.
```json
{
  "title": "수정된 제목",
  "content": "수정된 본문 내용입니다.",
  "board_id": 1,
  "attachments": ["file_id_A", "file_id_B"]
}
```
- **Status Codes**:
  - `204 No Content`
  - `401 Unauthorized` (로그인하지 않음)
  - `403 Forbidden` (게시글의 작성자가 아님)
  - `404 Not Found` (게시판이나 게시글이 존재하지 않음)
  - `410 Gone` (게시글이 삭제됨)
  
---

## Update Article by Executive (관리자에 의한 게시글 수정)

- **Method**: `POST`
- **URL**: `/api/executive/article/update/:id`
- **설명**: 게시글 수정
- **Request Body** (JSON):
  - attachments: optional
```json
{
  "title": "안녕하세요",
  "content": "## Hello?",
  "board_id": 1,
  "attachments": [
    {
      "id": 1,
      "article_id": 1,
      "file_id": "file_id"
    }
  ]
}
```
- **Status Codes**:
  - `204 No Content`
  - `401 Unauthorized` 
  - `403 Forbidden` 
  - `404 Not Found` (게시판이나 게시글이 존재하지 않음)
  - `410 Gone` (게시글이 삭제됨)
  
---

## Delete Article (작성자에 의한 게시글 삭제)

- **Method**: `POST`
- **URL**: `/api/article/delete/:id`
- **설명**: 작성자에 의한 게시글 삭제

- **Status Codes**:
  - `204 No Content`
  - `400 Bad Request` (board_id=1,2(sig/pig)일 때)
  - `401 Unauthorized` (로그인하지 않음)
  - `403 Forbidden` (게시글의 작성자가 아님)
  - `404 Not Found` (게시글이 존재하지 않음)

---

## Delete Article by Executive (관리자에 의한 게시글 삭제)

- **Method**: `POST`
- **URL**: `/api/executive/article/delete/:id`
- **설명**: 관리자에 의한 게시글 삭제

- **Status Codes**:
  - `204 No Content`
  - `401 Unauthorized` (로그인하지 않음)
  - `403 Forbidden` (권한 없음)
  - `404 Not Found` (게시글이 존재하지 않음)

---
