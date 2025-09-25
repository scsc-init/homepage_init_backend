# HTML 페이지 관련 DB, API 문서

**최신개정일:** 2025-09-23

# DB 구조

## HTML 메타데이터 DB

```sql
CREATE TABLE w_html_metadata (
    name TEXT PRIMARY KEY,
    size INTEGER NOT NULL CHECK (size >= 0),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    creator TEXT,

    FOREIGN KEY (creator) REFERENCES user(id) ON DELETE SET NULL
);
```

### SQL 관련
```sql
CREATE TRIGGER update_w_html_metadata_updated_at
AFTER UPDATE OF size, creator ON w_html_metadata 
FOR EACH ROW
BEGIN 
    UPDATE w_html_metadata SET updated_at = CURRENT_TIMESTAMP WHERE name = OLD.name; 
END;
```


# API 구조

## 파일 업로드 API (/api/executive/w, /api/w)

- 파일 업로드를 관리하는 API
- 업로드된 파일은 `.env`에 정의된 `W_HTML_DIR` 디렉토리에 저장

-----

## Upload File (Executive)

- **Method**: `POST`
- **URL**: `/api/executive/w/create`
- **Request Body** (multipart/form-data):
  - `file`: 업로드할 파일 (`UploadFile`). mime type이 `text/html`이고 확장자가 `.html`이어야 한다.
- **Response**:

```json
{
  "name": "scpc2025",
  "size": 23000,
  "created_at": "2025-03-01T10:00:00Z",
  "updated_at": "2025-04-01T12:00:00Z",
  "creator": "hash_of_creator_user"
}
```

- 파일의 이름으로 name이 지정된다. 파일명은 알파벳, 숫자, `_`, `-`으로만 구성되어야 한다.
- 파일의 크기(Bytes)가 size로 지정된다. 
- 파일을 업로드한 사람이 creator로 지정된다. 

* **Status Codes**:

  * `201 Created`
  * `400 Bad Request`: 파일 누락 또는 유효하지 않은 파일
  * `401 Unauthorized`: 로그인 하지 않음
  * `403 Forbidden`
  * `409 Conflict`: `name` 중복
  * `413 Payload Too Large`: 파일 크기 제한 초과(.env의 `FILE_MAX_SIZE`)
  * `422 Unprocessable Content`: 필드 누락 또는 유효하지 않은 값

---

## Read File

* **Method**: `GET`
* **URL**: `/api/w/:name`
* **설명**: 업로드된 파일을 이름으로 다운로드한다.

* **Path Parameters**:

  | 파라미터명 | 타입   | 설명               |
  | ----- | ---- | ---------------- |
  | `name`  | TEXT | 파일 이름 |

* **Response**:
  * **Content-Type**: `text/html`
  * 파일 바이너리 스트림


* **Status Codes**:

  * `200 OK` - 다운로드 성공
  * `404 Not Found` - 존재하지 않는 파일 `name`

---

## Get all metadatas (Executive)

- **Method**: `GET`
- **URL**: `/api/executive/ws`
- **Response**:

```json
[
  [
    {
        "size": 22531,
        "updated_at": "2025-09-24T08:38:05.318387",
        "name": "SCPC2",
        "created_at": "2025-09-24T08:38:05.318370",
        "creator": "hash_of_creator_user"
    },
    "name_of_creator_user"
  ],
  ...
]
```

* **Status Codes**:

  * `200 OK`
  * `401 Unauthorized`: 로그인 하지 않음
  * `403 Forbidden`

---

## Update File (Executive)

- **Method**: `POST`
- **URL**: `/api/executive/w/:name/update`
- **Request Body** (multipart/form-data):
  - `file`: 업로드할 파일 (`UploadFile`). mime type이 `text/html`이고 확장자가 `.html`이어야 한다. 
- **Response**:

```json
{
  "name": "scpc2025",
  "size": 23000,
  "created_at": "2025-03-01T10:00:00Z",
  "updated_at": "2025-04-01T12:00:00Z",
  "creator": "hash_of_creator_user"
}
```

- 기존 이름에 해당하는 파일을 업로드한 파일로 덮어쓴다. (업로드한 파일의 이름은 무관하다.)
- size, creator를 해당 요청에 맞게 갱신한다. 


* **Status Codes**:

  * `200 OK`
  * `401 Unauthorized`
  * `403 Forbidden`
  * `404 Not Found`: `name`에 해당하는 값이 없음.
  * `413 Payload Too Large`: 파일 크기 제한 초과(.env의 `FILE_MAX_SIZE`)

---


## Delete File (Executive)

- **Method**: `POST`
- **URL**: `/api/executive/w/:name/delete`
- **Response**:

* **Status Codes**:

  * `204 No Content`
  * `401 Unauthorized`
  * `403 Forbidden`
  * `404 Not Found`: `name`에 해당하는 값이 없음.

---
