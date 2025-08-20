# 게시글 관련 DB, API 명세서
**최신개정일:** 2025-07-07

# DB 구조

## 댓글 DB
```sql
CREATE TABLE "comment" (
    "id" INTEGER,
    "content" TEXT NOT NULL,
    "author_id" TEXT NOT NULL,
    "article_id" INTEGER NOT NULL,
    "parent_id" INTEGER,
    "is_deleted" INTEGER NOT NULL DEFAULT 0,
    "created_at" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "deleted_at" DATETIME,
    PRIMARY KEY("id" AUTOINCREMENT),
    FOREIGN KEY("author_id") REFERENCES "user"("id") ON DELETE RESTRICT,
    FOREIGN KEY("article_id") REFERENCES "article"("id") ON DELETE CASCADE,
    FOREIGN KEY("parent_id") REFERENCES "comment"("id") ON DELETE SET NULL
);
```
```sqlite
CREATE INDEX idx_article_id ON comment(article_id);
CREATE INDEX idx_parent_id ON comment(parent_id);
```

# API 구조

## 댓글 관련 API(/api/comment)

- 댓글 정보를 관리하는 API

## Create Comment (댓글 생성)

- **Method**: `POST`
- **URL**: `/api/comment/create`
- **설명**: 댓글 생성
- **Request Body** (JSON):
```json
{
  "content": "Nice.",
  "article_id": 1,
  "parent_id": null
}
```
- **Response**:
```json
{
  "id": 1,
  "content": "Nice.",
  "author_id": "",
  "article_id": 1,
  "parent_id": null,
  "is_deleted": 0,
  "created_at": "2025-07-01T12:00:00",
  "updated_at": "2025-07-01T12:00:00",
  "deleted_at": null
}
```
- **Status Codes**:
  - `201 Created`
  - `401 Unauthorized` (로그인하지 않음)
  - `403 Forbidden` (권한 없음)
  - `404 Not Found` (게시판이나 게시글이 존재하지 않음)
  - `409 Conflict` (중복 데이터 삽입)
  
---

## Get Comments List (댓글 목록 조회)

- **Method**: `GET`
- **URL**: `/api/comments/:article_id`
- **설명**: 댓글 목록 조회, 댓글이 삭제된 경우 `content`=`null`
- **Response**:
```json
[
  {
  "id": 1,
  "content": "Nice.",
  "author_id": "",
  "article_id": 1,
  "parent_id": null,
  "is_deleted": 0,
  "created_at": "2025-07-01T12:00:00",
  "updated_at": "2025-07-01T12:00:00",
  "deleted_at": null
  }
]
```
- **Status Codes**:
  - `200 OK`
  - `404 Not Found` (게시판이나 게시글이 존재하지 않음)

---

## Get Comment by ID (ID로 댓글 조회)

- **Method**: `GET`
- **URL**: `/api/comment/:id`
- **설명**: 해당 ID의 댓글 조회, 댓글이 삭제된 경우 `content`=`null`
- **Response**:
```json
{
  "id": 1,
  "content": "Nice.",
  "author_id": "",
  "article_id": 1,
  "parent_id": null,
  "is_deleted": 0,
  "created_at": "2025-07-01T12:00:00",
  "updated_at": "2025-07-01T12:00:00",
  "deleted_at": null
}
```
- **Status Codes**:
  - `200 OK`
  - `404 Not Found` (댓글이 존재하지 않음)

---

## Update Comment (댓글 수정)

- **Method**: `POST`
- **URL**: `/api/comment/update/:id`
- **설명**: 댓글 수정
- **Request Body** (JSON):
```json
{
  "content": "Isn't nice."
}
```
- **Status Codes**:
  - `204 No Content`
  - `401 Unauthorized` (로그인하지 않음)
  - `403 Forbidden` (댓글의 작성자가 아님)
  - `404 Not Found` (댓글이 존재하지 않음)
  - `410 Gone` (댓글이 삭제됨)
  
---

## Delete Comment by Author (작성자에 의한 댓글 삭제)

- **Method**: `POST`
- **URL**: `/api/comment/delete/:id`
- **설명**: 작성자에 의한 댓글 삭제

- **Status Codes**:
  - `204 No Content`
  - `401 Unauthorized` (로그인하지 않음)
  - `403 Forbidden` (댓글의 작성자가 아님)
  - `404 Not Found` (댓글이 존재하지 않음)
  - `410 Gone` (이미 삭제됨)

---

## Delete Comment by Executive (관리자에 의한 댓글 삭제)

- **Method**: `POST`
- **URL**: `/api/executive/comment/delete/:id`
- **설명**: 관리자에 의한 댓글 삭제

- **Status Codes**:
  - `204 No Content`
  - `401 Unauthorized` (로그인하지 않음)
  - `403 Forbidden` (권한 없음)
  - `404 Not Found` (댓글이 존재하지 않음)
  - `410 Gone` (이미 삭제됨)

---

