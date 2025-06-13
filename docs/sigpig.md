# SIG/PIG 관련 DB, API 명세서
**최신개정일:** 2025-05-16

# DB 구조

## SIG/PIG DB
```sql
CREATE TABLE sig (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    content_id INTEGER UNIQUE,
    status TEXT NOT NULL CHECK (status IN ('surveying', 'recruiting', 'active', 'inactive')),
    year INTEGER NOT NULL CHECK (year >= 2025),
    semester INTEGER NOT NULL CHECK (semester IN (1, 2)),

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    owner TEXT NOT NULL,
    UNIQUE (title, year, semester),
    FOREIGN KEY (owner) REFERENCES user(id) ON DELETE RESTRICT,
    FOREIGN KEY (content_id) REFERENCES article(id) ON DELETE SET NULL
);
```

```sql
CREATE TABLE pig (
    ... -- same as sig
);
```

## SIG/PIG MEMBER DB
```sql
CREATE TABLE sig_member (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ig_id INTEGER NOT NULL,
    user_id TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('surveying', 'recruiting', 'active', 'inactive')),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (ig_id, user_id, status),
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (ig_id) REFERENCES sig(id) ON DELETE CASCADE
);
```

```sql
CREATE TABLE pig_member (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ig_id INTEGER NOT NULL,
    user_id TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('surveying', 'recruiting', 'active', 'inactive')),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (ig_id, user_id, status),
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (ig_id) REFERENCES pig(id) ON DELETE CASCADE
);
```

## SIG/PIG Global Status
```sql
CREATE TABLE sig_global_status (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    status TEXT NOT NULL CHECK (status IN ('surveying', 'recruiting', 'active', 'inactive')),
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE pig_global_status (
    ... -- same as sig
);
```

## SQL 관련
```sql
CREATE INDEX idx_sig_owner ON sig(owner);
CREATE INDEX idx_sig_term ON sig(year, semester);
CREATE INDEX idx_sig_member_user ON sig_member(user_id);
CREATE INDEX idx_sig_member_ig ON sig_member(ig_id);
CREATE INDEX idx_pig_member_user ON pig_member(user_id);
CREATE INDEX idx_pig_member_ig ON pig_member(ig_id);
```

```sql
CREATE TRIGGER update_sig_updated_at
AFTER UPDATE ON sig
FOR EACH ROW
WHEN 
    OLD.title != NEW.title OR
    OLD.description != NEW.description OR
    OLD.content_id != NEW.content_id OR
    OLD.status != NEW.status OR
    OLD.year != NEW.year OR
    OLD.semester != NEW.semester OR
    OLD.owner != NEW.owner
BEGIN
    UPDATE sig
    SET updated_at = CURRENT_TIMESTAMP
    WHERE id = OLD.id;
END;

CREATE TRIGGER update_pig_updated_at
AFTER UPDATE ON pig
FOR EACH ROW
WHEN 
    OLD.title != NEW.title OR
    OLD.description != NEW.description OR
    OLD.content_id != NEW.content_id OR
    OLD.status != NEW.status OR
    OLD.year != NEW.year OR
    OLD.semester != NEW.semester OR
    OLD.owner != NEW.owner
BEGIN
    UPDATE pig
    SET updated_at = CURRENT_TIMESTAMP
    WHERE id = OLD.id;
END;

CREATE TRIGGER update_sig_global_status_updated_at
AFTER UPDATE ON sig_global_status
FOR EACH ROW
WHEN 
    OLD.status != NEW.status
BEGIN
    UPDATE sig_global_status
    SET updated_at = CURRENT_TIMESTAMP
    WHERE id = OLD.id;
END;

CREATE TRIGGER update_pig_global_status_updated_at
AFTER UPDATE ON pig_global_status
FOR EACH ROW
WHEN 
    OLD.status != NEW.status
BEGIN
    UPDATE pig_global_status
    SET updated_at = CURRENT_TIMESTAMP
    WHERE id = OLD.id;
END;
```

# API 구조

## SIG 관련 API(/api/sig)

- 시그 정보를 관리하는 API
- 시그장은 사용자 테이블과 외래 키로 연결됨
- 시그 구성원은 시그 테이블, 사용자 테이블과 외래 키로 연결됨

---

## 🔹 Create SIG

* **Method**: `POST`
* **URL**: `/api/sig/create`
* 로그인한 사용자가 owner가 됨
* **Request Body** (JSON):

```json
{
  "title": "AI SIG",
  "description": "인공지능을 연구하는 소모임입니다.",
  "content": "## 안녕하세요",
  "year": 2025,
  "semester": 1
}
```

* **Response**:

```json
{
  "id": 1,
  "title": "AI SIG",
  "description": "인공지능을 연구하는 소모임입니다.",
  "content_id": 1,
  "status": "surveying",
  "year": 2025,
  "semester": 1,
  "created_at": "2025-03-01T10:00:00Z",
  "updated_at": "2025-04-01T12:00:00Z",
  "owner": "hash_of_owner_user"
}
```

* **Status Codes**:

  * `201 Created`
  * `400 Bad Request`: sig global status가 surveying이 아닐 때
  * `401 Unauthorized`: 로그인 하지 않음
  * `409 Conflict`: `title`, `year`, `semester` 중복
  * `422 Unprocessable Content`: 필드 누락 또는 유효하지 않은 값

---

## 🔹 Get SIG by ID

* **Method**: `GET`
* **URL**: `/api/sig/:id`
* **Response**:

```json
{
  "id": 1,
  "title": "AI SIG",
  "description": "인공지능을 연구하는 소모임입니다.",
  "content_id": 1,
  "status": "active",
  "year": 2025,
  "semester": 1,
  "created_at": "2025-03-01T10:00:00Z",
  "updated_at": "2025-04-01T12:00:00Z",
  "owner": "hash_of_owner_user"
}
```

* **Status Codes**:

  * `200 OK`
  * `404 Not Found`: 해당 SIG가 존재하지 않음

---

## 🔹 Get All SIGs

* **Method**: `GET`
* **URL**: `/api/sigs`
* **Response**:

```json
[
  {
    "id": 1,
    "title": "AI SIG",
    "description": "인공지능을 연구하는 소모임입니다.",
    "content_id": 1,
    "status": "active",
    "year": 2025,
    "semester": 1,
    "created_at": "2025-03-01T10:00:00Z",
    "updated_at": "2025-04-01T12:00:00Z",
    "owner": "hash_of_owner_user"
  },
  ...
]
```

* **Status Codes**:

  * `200 OK`

---

## 🔹 Update SIG (Owner Only)

* **Method**: `POST`
* **URL**: `/api/sig/:id/update`
* **Request Body** (JSON):

```json
{
  "title": "AI SIG",
  "description": "업데이트된 설명입니다.",
  "content": "### 안녕하세요",
  "year": 2025,
  "semester": 1
}
```

- 일부만 포함하여 요청을 보내도 된다
- content가 포함된다면, 새로운 article을 생성하여 content_id가 바뀐다

* **Status Codes**:

  * `204 No Content`
  * `401 Unauthorized`
  * `403 Forbidden`: 권한 없음
  * `404 Not Found`
  * `409 Conflict`: `title`, `year`, `semester` 중복
  * `422 Unprocessable Content`

---

## 🔹 Delete SIG (Owner Only)

* **Method**: `POST`
* **URL**: `/api/sig/:id/delete`

* **Status Codes**:

  * `204 No Content`
  * `401 Unauthorized`
  * `403 Forbidden`
  * `404 Not Found`

---

## 🔹 Transfer SIG Ownership(Owner / Executive)

* **Method**: `POST`
* **URL**: `/api/sig/:id/handover`
* **Request Body** (JSON):

```json
{
  "new_owner": "hash_of_new_owner"
}
```

* **Status Codes**:

  * `204 No Content`: 소유자 변경 성공
  * `401 Unauthorized`
  * `403 Forbidden`
  * `404 Not Found`: SIG 존재하지 않음 / 사용자 존재하지 않음
  * `422 Unprocessable Content`

---

## 🔹 Update SIG (Executive)

* **Method**: `POST`
* **URL**: `/api/executive/sig/:id/update`
* **Request Body**: 

```json
{
  "title": "AI SIG",
  "description": "업데이트된 설명입니다.",
  "content": "### 안녕하세요",
  "status": "recruiting",
  "year": 2025,
  "semester": 1
}
```

- 일부만 포함하여 요청을 보내도 된다
- content가 포함된다면, 새로운 article을 생성하여 content_id가 바뀐다

* **Status Codes**:

  * `204 No Content`
  * `401 Unauthorized`
  * `403 Forbidden`
  * `404 Not Found`
  * `409 Conflict`: `title`, `year`, `semester` 중복

---

## 🔹 Delete SIG (Executive)

* **Method**: `POST`
* **URL**: `/api/executive/sig/:id/delete`

* **Status Codes**:

  * `204 No Content`
  * `401 Unauthorized`
  * `403 Forbidden`
  * `404 Not Found`

---

## 🔹 Get SIG Members

* **Method**: `GET`
* **URL**: `/api/sig/:id/members`
* **Response**:

```json
[
  {
    "id": 1,
    "ig_id": 1,
    "user_id": "hash_of_user"
  },
  ...
]
```

* **Status Codes**:

  * `200 OK`
  * `404 Not Found`

---

## 🔹 Join SIG (Current User)

* **Method**: `POST`
* **URL**: `/api/sig/:id/member/join`

* **Status Codes**:

  * `204 No Content`
  * `400 Bad Request`: sig global status가 surveying/recruiting이 아닐 때
  * `401 Unauthorized`
  * `409 Conflict`: 이미 가입됨

---

## 🔹 Leave SIG (Current User)

* **Method**: `POST`
* **URL**: `/api/sig/:id/member/leave`

* **Status Codes**:

  * `204 No Content`
  * `401 Unauthorized`
  * `404 Not Found`: 가입되어 있지 않음
  * `409 Conflict`: 시그장 탈퇴 불가

---

## 🔹 Join SIG (Executive)

* **Method**: `POST`
* **URL**: `/api/executive/sig/:id/member/join`
* **Request Body**:

```json
{
  "user_id": "hash_of_user"
}
```

* **Status Codes**:

  * `204 No Content`
  * `401 Unauthorized`
  * `403 Forbidden`
  * `404 Not Found`
  * `409 Conflict`

---

## 🔹 Leave SIG Member (Executive)

* **Method**: `POST`
* **URL**: `/api/executive/sig/:id/member/leave`
* **Request Body**:

```json
{
  "user_id": "hash_of_user"
}
```

* **Status Codes**:

  * `204 No Content`
  * `401 Unauthorized`
  * `403 Forbidden`
  * `404 Not Found`
  * `409 Conflict`: 시그장 탈퇴 불가

---

## 🔹 Get Global SIG Status

* **Method**: `GET`
* **URL**: `/api/sig/global/status`

* **Response Body**:

```json
{
  "status": "active"
}
```

* **Status Codes**:
  * `200 OK` - 상태 변경 성공

---

## 🔹 Update Global SIG Status

* **Method**: `POST`
* **URL**: `/api/executive/sig/global/status`
* **설명**: 임원이 전체 SIG의 상태를 일괄적으로 설정합니다

* **Request Body**:

```json
{
  "status": "active"
}
```
status는 ('surveying', 'recruiting', 'active', 'inactive') 중 하나
* **유효한 status 변경 방법**

|기존 status|변경 status|
|---|---|
|inactive|surveying|
|surveying|recruiting|
|recruiting|active|
|any|inactive|

* **Status Codes**:

  * `204 No Content` - 상태 변경 성공
  * `400 Bad Request` - 유효하지 않은 `status` 변경
  * `401 Unauthorized` - 인증 실패
  * `403 Forbidden` - 권한 없음 (임원이 아닌 경우)

---

## PIG 관련 API(/api/pig)
`/api/sig`에서 `sig`를 `pig`로 바꾼다
