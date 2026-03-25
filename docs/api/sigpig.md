# SIG/PIG 관련 DB, API 명세서
**최신개정일:** 2026-02-12

# DB 구조

## SIG/PIG DB
```sql
CREATE TABLE sig (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    content_id INTEGER NOT NULL UNIQUE,
    status TEXT NOT NULL CHECK (status IN ('surveying', 'recruiting', 'active', 'inactive')),
    year INTEGER NOT NULL CHECK (year >= 2025),
    semester INTEGER NOT NULL CHECK (semester IN (1, 2, 3, 4)),
    created_year INTEGER NOT NULL CHECK (created_year >= 2025),
    created_semester INTEGER NOT NULL CHECK (created_semester IN (1, 2, 3, 4)),

    should_extend BOOLEAN NOT NULL DEFAULT FALSE,
    is_rolling_admission BOOLEAN NOT NULL DEFAULT FALSE,

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    owner TEXT NOT NULL,
    UNIQUE(created_year, created_semester, title),
    UNIQUE (title, year, semester),
    FOREIGN KEY (owner) REFERENCES user(id) ON DELETE RESTRICT,
    FOREIGN KEY (content_id) REFERENCES article(id) ON DELETE RESTRICT
);
```
- status 중 'surveying'은 더 이상 사용하지 않습니다. 기존 'surveying'은 모두 'recruiting'으로 변경됩니다. 
- `created_year`, `created_semester`: SIG가 **처음 생성된 학기**. 이후 변경되지 않습니다.  
- `year`, `semester`: SIG가 **현재 속한 학기(운영/종료 학기)**. 학기 이월 시 이 값만 업데이트됩니다.  


```sql
CREATE TABLE pig (
    ... -- same as sig
    is_rolling_admission TEXT DEFAULT 'during_recruiting' NOT NULL CHECK (is_rolling_admission IN ('always', 'never', 'during_recruiting')),
    ... -- same as sig
);
```

- `is_rolling_admission` 기본값은 `"during_recruiting"`입니다.

## SIG/PIG MEMBER DB
```sql
CREATE TABLE sig_member (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ig_id INTEGER NOT NULL,
    user_id TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (ig_id, user_id),
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (ig_id) REFERENCES sig(id) ON DELETE CASCADE
);
```

```sql
CREATE TABLE pig_member (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ig_id INTEGER NOT NULL,
    user_id TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (ig_id, user_id),
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (ig_id) REFERENCES pig(id) ON DELETE CASCADE
);
```

## SIG/PIG Website
```sql
CREATE TABLE public.sig_website (
    id BIGSERIAL PRIMARY KEY,
    sig_id bigint NOT NULL REFERENCES public.sig(id) ON DELETE CASCADE,
    label text NOT NULL,
    url text NOT NULL,
    sort_order bigint NOT NULL DEFAULT '0'::bigint,
    created_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

## SQL 관련
```sql
CREATE INDEX idx_sig_owner ON sig(owner);
CREATE INDEX idx_sig_term ON sig(year, semester);
CREATE INDEX idx_pig_owner ON pig(owner);
CREATE INDEX idx_pig_term ON pig(year, semester);
CREATE INDEX idx_sig_member_user ON sig_member(user_id);
CREATE INDEX idx_sig_member_ig ON sig_member(ig_id);
CREATE INDEX idx_pig_member_user ON pig_member(user_id);
CREATE INDEX idx_pig_member_ig ON pig_member(ig_id);
```

```sql
CREATE TRIGGER update_sig_updated_at
AFTER UPDATE OF title, description, content_id, status, year, semester, owner, should_extend, is_rolling_admission ON sig 
FOR EACH ROW
BEGIN 
    UPDATE sig SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id; 
END;

CREATE TRIGGER update_pig_updated_at
AFTER UPDATE OF title, description, content_id, status, year, semester, owner, should_extend, is_rolling_admission ON pig 
FOR EACH ROW
BEGIN 
    UPDATE pig SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id; 
END;

```

# API 구조

## SIG 관련 API(/api/sig)

- 시그 정보를 관리하는 API
- 시그장은 사용자 테이블과 외래 키로 연결됨
- 시그 구성원은 시그 테이블, 사용자 테이블과 외래 키로 연결됨
- 응답 형식은 [/src/schemas/sig.py](/src/schemas/sig.py) 참고하십시오

---

## Create SIG

* **Method**: `POST`
* **URL**: `/api/sig/create`
* 로그인한 사용자가 owner가 됨
* **Request Body** (JSON):

```json
{
  "title": "AI SIG",
  "description": "인공지능을 연구하는 소모임입니다.",
  "content": "## 안녕하세요",
  "is_rolling_admission": false,
  "websites": []
}
```

websites가 포함된다면, 기존의 websites는 모두 삭제되고 새로운 websites로 대체된다.

* **Response**: `SigResponse`
* **Status Codes**:

  * `201 Created`
  * `400 Bad Request`: sig global status가 recruiting이 아닐 때
  * `401 Unauthorized`: 로그인 하지 않음
  * `409 Conflict`: `title`, `year`, `semester` 중복
  * `422 Unprocessable Content`: 필드 누락 또는 유효하지 않은 값

---

## Get SIG by ID

* **Method**: `GET`
* **URL**: `/api/sig/:id`
* **Response**: `SigResponse`
* **Status Codes**:

  * `200 OK`
  * `404 Not Found`: 해당 SIG가 존재하지 않음

---

## Get All SIGs

* **Method**: `GET`
* **URL**: `/api/sigs`
* **Query Parameters**: all optional
  * `year`: `int`
  * `semester`: `int`
  * `status`: `str`
  * `tag`: `str` (repeatable)
* **Example Request**:
  * `/api/sigs?year=2025&semester=3&status=active`
  * `/api/sigs?tag=SIG&tag=PS`
* **Response**: `Sequence[SigResponse]`
* **Status Codes**:
  * `200 OK`

* **Notes**:
  * 각 원소는 `tags` 필드를 포함한다
  * `tag` 쿼리 파라미터는 다중 선택 가능
  * 선택된 여러 태그는 **AND 조건**으로 적용된다
  * 예: `SIG`, `PS`를 동시에 선택하면 두 태그를 모두 가진 SIG만 표시된다
  * URL 쿼리 파라미터는 `?tag=SIG&tag=PS` 형태로 사용한다

---

## Update SIG (Owner Only)

* **Method**: `POST`
* **URL**: `/api/sig/:id/update`
* **Request Body** (JSON):

```json
{
  "title": "AI SIG",
  "description": "업데이트된 설명입니다.",
  "content": "### 안녕하세요",
  "should_extend": true,
  "is_rolling_admission": true,
  "websites": []
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

## Delete SIG (Owner Only)

* **Method**: `POST`
* **URL**: `/api/sig/:id/delete`

* **Status Codes**:

  * `204 No Content`
  * `401 Unauthorized`
  * `403 Forbidden`
  * `404 Not Found`

---

## Transfer SIG Ownership

### Owner Initiated

* **Method**: `POST`
* **URL**: `/api/sig/:id/handover`
* **Request Body** (JSON):

```json
{
  "new_owner": "hash_of_new_owner"
}
```

* **Notes**:
  * 새로운 소유자는 해당 SIG의 구성원이어야 하며 기존 소유자와 달라야 함
  * 요청자는 현재 SIG장과 동일해야 함
* **Status Codes**:

  * `204 No Content`: 소유자 변경 성공
  * `400 Bad Request`: 새로운 소유자가 기존 소유자와 동일함
  * `401 Unauthorized`
  * `403 Forbidden`: 요청자가 SIG장이 아님
  * `404 Not Found`: SIG / 사용자 / 구성원 정보가 존재하지 않음
  * `422 Unprocessable Content`

### Executive Initiated

* **Method**: `POST`
* **URL**: `/api/executive/sig/:id/handover`
* **Request Body** (JSON):

```json
{
  "new_owner": "hash_of_new_owner"
}
```

* **Notes**:
  * 임원진이 강제 양도할 때 사용
  * 새로운 소유자는 해당 SIG의 구성원이어야 하며 기존 소유자와 달라야 함
* **Status Codes**:

  * `204 No Content`: 소유자 변경 성공
  * `400 Bad Request`: 새로운 소유자가 기존 소유자와 동일함
  * `401 Unauthorized`
  * `403 Forbidden`: 임원 권한 없음
  * `404 Not Found`: SIG / 사용자 / 구성원 정보가 존재하지 않음
  * `422 Unprocessable Content`

---

## Update SIG (Executive)

* **Method**: `POST`
* **URL**: `/api/executive/sig/:id/update`
* **Request Body**: 

```json
{
  "title": "AI SIG",
  "description": "업데이트된 설명입니다.",
  "content": "### 안녕하세요",
  "status": "recruiting",
  "should_extend": true,
  "is_rolling_admission": true,
  "websites": []
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

## Delete SIG (Executive)

* **Method**: `POST`
* **URL**: `/api/executive/sig/:id/delete`

* **Status Codes**:

  * `204 No Content`
  * `401 Unauthorized`
  * `403 Forbidden`
  * `404 Not Found`

---

## Get SIG Members

* **Method**: `GET`
* **URL**: `/api/sig/:id/members`
* **Response**:

```json
[
  {
    "id": 1,
    "ig_id": 1,
    "user_id": "b4c9a289323b21a01c3e940f150eb9b8c542587f1abfd8f0e1cc1ffc5e475514",
    "user": {
      "id": "b4c9a289323b21a01c3e940f150eb9b8c542587f1abfd8f0e1cc1ffc5e475514",
      "email": "user@example.com",
      "name": "홍길동",
      "major_id": 1
    }
  },
  ...
]
```

* **Status Codes**:

  * `200 OK`
  * `404 Not Found`

---

## Join SIG (Current User)

* **Method**: `POST`
* **URL**: `/api/sig/:id/member/join`

* **Status Codes**:

  * `204 No Content`
  * `400 Bad Request`: sig 상태가 가입 가능한 상태가 아닐 때
    * sig의 `is_rolling_admission`이 `true`이면 `recruiting`, `active`일 때 가입 가능
    * sig의 `is_rolling_admission`이 `false`이면 `recruiting`일 때 가입 가능
  * `401 Unauthorized`
  * `409 Conflict`: 이미 가입됨

---

## Leave SIG (Current User)

* **Method**: `POST`
* **URL**: `/api/sig/:id/member/leave`

* **Status Codes**:

  * `204 No Content`
  * `401 Unauthorized`
  * `404 Not Found`: 가입되어 있지 않음
  * `409 Conflict`: 시그장 탈퇴 불가

---

## Join SIG (Executive)

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

## Leave SIG Member (Executive)

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



## 시그 태그 기능(SIG Only)
### 시그 태그 추가

시그에 기존 태그를 추가한다.

* **Method**: `POST`
* **URL**: `/api/sig/:id/tag`

* **Request Body**:

```json
{
  "tag_id": 3
}
```

* **Response Body**:

```json
{
  "id": 1,
  "sig_id": 1,
  "tag_id": 3,
  "created_at": "2025-03-01T10:00:00Z"
}
```

* **권한**
  * 시그 소유자 또는 운영진 이상 가능
  * `is_major=true` 태그는 운영진 이상만 추가 가능

* **Status Codes**:
  * `201 Created`
  * `403 Forbidden`
  * `404 Not Found`
  * `409 Conflict`

---

### 시그 태그 목록 조회

특정 시그에 등록된 모든 태그 목록을 조회한다.

* **Method**: `GET`
* **URL**: `/api/sig/:id/tag`

* **Response Body**:

```json
[
  {
    "id": 1,
    "text": "SIG",
    "is_major": true,
    "created_at": "2025-03-01T10:00:00Z"
  },
  {
    "id": 2,
    "text": "애드혹",
    "is_major": false,
    "created_at": "2025-03-01T10:00:00Z"
  }
]
```

* **Status Codes**:
  * `200 OK`
  * `404 Not Found`

---

### 시그 태그 삭제

시그에 등록된 특정 태그를 삭제한다.

* **Method**: `DELETE`
* **URL**: `/api/sig/:id/tag/:tag_id`

* **권한**
  * 시그 소유자 또는 운영진 이상 가능
  * `is_major=true` 태그는 운영진 이상만 삭제 가능

* **동작**
  * 태그가 어떤 시그에도 더 이상 연결되어 있지 않으면 태그 자체도 자동 삭제됨
  * 자동 삭제 대상은 non-major 태그만 해당

* **Status Codes**:
  * `204 No Content`
  * `403 Forbidden`
  * `404 Not Found`

---

### 태그 생성 (Current User)

일반 사용자가 non-major 태그를 생성한다.

* **Method**: `POST`
* **URL**: `/api/tag`

* **Request Body**:

```json
{
  "text": "군대"
}
```

* **Response Body**:

```json
{
  "id": 5,
  "text": "군대",
  "is_major": false,
  "created_at": "2025-03-01T10:00:00Z"
}
```

* **Status Codes**:
  * `201 Created`
  * `401 Unauthorized`
  * `409 Conflict`
  * `422 Unprocessable Content`

---

### 태그 생성 (Executive)

운영진이 태그를 생성한다.

* **Method**: `POST`
* **URL**: `/api/executive/tag`

* **Request Body**:

```json
{
  "text": "SIG",
  "is_major": true
}
```

* **Response Body**:

```json
{
  "id": 1,
  "text": "SIG",
  "is_major": true,
  "created_at": "2025-03-01T10:00:00Z"
}
```

* **Status Codes**:
  * `201 Created`
  * `401 Unauthorized`
  * `403 Forbidden`
  * `409 Conflict`
  * `422 Unprocessable Content`

---

### 태그 삭제 (Executive)

운영진이 태그 자체를 삭제한다.

* **Method**: `DELETE`
* **URL**: `/api/executive/tag/:tag_id`

* **동작**
  * 해당 태그가 연결된 모든 SIG에서 태그 연결도 함께 제거됨

* **Status Codes**:
  * `204 No Content`
  * `401 Unauthorized`
  * `403 Forbidden`
  * `404 Not Found`

---


## PIG 관련 API(/api/pig)
`/api/sig`에서 `sig`를 `pig`로 바꾼다

### 예외 사항

* 시그와 구조가 다른 피그만의 API 예외 사항은 아래와 같다.
* 피그는 `is_rolling_admission` 이 Boolean 이 아니라 String 타입이며 `always`, `never`, `during_recruiting`의 세 가지 경우가 존재한다.
* 응답 형식은 [/src/schemas/pig.py](/src/schemas/pig.py) 참고하십시오

---

## Create PIG

* **Method**: `POST`
* **URL**: `/api/pig/create`
* 로그인한 사용자가 owner가 됨
* **Request Body** (JSON):

```json
{
  "title": "AI PIG",
  "description": "인공지능을 연구하는 소모임입니다.",
  "content": "## 안녕하세요",
  "is_rolling_admission": "during_recruiting",
  "websites": [
    {
      "label": "GitHub",
      "url": "https://github.com/aipig",
      "sort_order": 1,
    }
  ]
}
```

* **Response**: `PigResponse`
* **Status Codes**:
  * `201 Created`
  * `400 Bad Request`: pig global status가 recruiting이 아닐 때
  * `401 Unauthorized`: 로그인 하지 않음
  * `409 Conflict`: `title`, `year`, `semester` 중복
  * `422 Unprocessable Content`: 필드 누락 또는 유효하지 않은 값

---

## Get PIG by ID

* **Method**: `GET`
* **URL**: `/api/pig/:id`
* **Response**: `PigResponse`
* **Status Codes**:
  * `200 OK`
  * `404 Not Found`: 해당 PIG가 존재하지 않음

---

## Get All PIGs

* **Method**: `GET`
* **URL**: `/api/pigs`
* **Query Parameters**: all optional
  * `year`: `int`
  * `semester`: `int`
  * `status` `str`
* **Example Request**:
  * `/api/pigs?year=2025&semester=3&status=active`
* **Response**: `Sequence[PigResponse]`
* **Status Codes**:
  * `200 OK`


---

## Update PIG

* **Method**: `POST`
* **URL**: `/api/pig/:id/update` (for owner) / `/api/executive/pig/:id/update` (for executive)
* **Request Body** (JSON):

```json
{
  "title": "AI PIG",
  "description": "업데이트된 설명입니다.",
  "content": "### 안녕하세요",
  "should_extend": true,
  "is_rolling_admission": "during_recruiting",
  "websites": [
    {
      "label": "GitHub",
      "url": "https://github.com/aipig",
      "sort_order": 1,
    }
  ]
}
```

- 일부만 포함하여 요청을 보내도 된다
- content가 포함된다면, 새로운 article을 생성하여 content_id가 바뀐다
- websites가 포함된다면, 기존의 websites는 모두 삭제되고 새로운 websites로 대체된다. 

* **Status Codes**:

  * `204 No Content`
  * `401 Unauthorized`
  * `403 Forbidden`: 권한 없음
  * `404 Not Found`
  * `409 Conflict`: `title`, `year`, `semester` 중복
  * `422 Unprocessable Content`

---


## Join PIG (Current User)

* **Method**: `POST`
* **URL**: `/api/pig/:id/member/join`

* **Status Codes**:

  * `204 No Content`
  * `400 Bad Request`: pig 상태가 가입 가능한 상태가 아닐 때
    * pig의 `is_rolling_admission`이 `always`이면 `recruiting`, `active`일 때 가입 가능
    * pig의 `is_rolling_admission`이 `during_recruiting`이면 `recruiting`일 때 가입 가능
    * pig의 `is_rolling_admission`이 `never`이면 가입 불가능
  * `401 Unauthorized`
  * `409 Conflict`: 이미 가입됨

---
