# 회원 관련 DB, API 명세서

> 최초작성일: 2025-05-01  
> 최신개정일: 2025-09-05  
> 최신개정자: 이한경  
> 작성자: 이한경, 윤영우  

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
    status TEXT DEFAULT 'standby' NOT NULL CHECK (status IN ('active', 'pending', 'standby', 'banned')),
    discord_id INTEGER UNIQUE DEFAULT NULL,
    discord_name TEXT UNIQUE DEFAULT NULL,
    profile_picture TEXT,
    profile_picture_is_url BOOLEAN NOT NULL DEFAULT FALSE,

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
- profile_picture에는 파일 위치(ex. `static/image/pfps/asdf.png`) 또는 이미지 URL이 들어가며, 전자의 경우 profile_picture_is_url이 false, 후자의 경우 true이다. 단, default값은 null이며 이 경우 프론트엔드에서 default 이미지로 처리한다.
- status는 [`check_user_status_rule`](./common.md) 테이블에서도 사용한다. 

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
    OLD.discord_id != NEW.discord_id OR
    OLD.discord_name != NEW.discord_name OR
    OLD.major_id != NEW.major_id
BEGIN
    UPDATE user
    SET updated_at = CURRENT_TIMESTAMP
    WHERE id = OLD.id;
END;

CREATE INDEX idx_user_major ON user(major_id);
CREATE INDEX idx_user_role ON user(role);
```

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

## standby request DB
```sql
CREATE TABLE standby_req_tbl (
    standby_user_id TEXT PRIMARY KEY,
    user_name TEXT NOT NULL,
    deposit_name TEXT NOT NULL,
    deposit_time DATETIME,
    is_checked BOOLEAN NOT NULL DEFAULT 0,
    FOREIGN KEY (standby_user_id) REFERENCES user(id) ON DELETE RESTRICT
);
```
- `deposit_name`은 입금자명으로, "이름"+"전화번호 뒤 2자리"로 설정한다.

# API 구조

## 회원 관련 API(/api/user)

- 회원 정보를 관리하는 API
- 회원은 이메일, 이름, 전화번호, 전공 등을 포함하고 있으며, 전공은 `major` 테이블과 외래 키 관계로 연결됨

---

## Create User (회원 등록)

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
  "major_id": 1,
  "profile_picture": "https://google.oauth.etc",
  "profile_picture_is_url": true,
  "hashToken": "some-hash-token"
}
```
- `profile_picture`은 구글 oauth에서 반환된 프로필 사진 URL이 기본으로 전송된다.
- **Response**:
```json
{
  "id": "b4c9a289323b21a01c3e940f150eb9b8c542587f1abfd8f0e1cc1ffc5e475514",
  "email": "user@example.com",
  "name": "홍길동",
  "phone": "01012345678",
  "student_id": "202312345",
  "role": 200,
  "status": "standby",
  "discord_id": null,
  "discord_name": null,
  "major_id": 1,
  "profile_picture": "https://google.oauth.etc",
  "profile_picture_is_url": true,
  "last_login": "2025-04-01T12:00:00",
  "created_at": "2025-04-01T12:00:00",
  "updated_at": "2025-04-01T12:00:00",
}
```
- **Status Codes**:
  - `201 Created`
  - `400 Bad Request` (유효하지 않은 이미지 url)
  - `401 Unauthorized` (인증 실패 시)
  - `409 Conflict` (UNIQUE 필드 중복)
  - `422 Unprocessable Content` (오류, 제약 위반 등)

---

## Enroll User (사용자 등록)

* **Method**: `POST`
* **URL**: `/api/user/enroll`
* **설명**: `pending` 또는 `standby` 상태의 사용자를 `active` 상태로 등록(활성화)하기 위한 `standby_req_tbl` 대기열에 등록하고 상태를 `standby`로 변경합니다. 이 엔드포인트는 로그인된 사용자의 현재 상태를 변경하는 데 사용됩니다.
* **Status Codes**:
  * `204 No Content`: 사용자가 성공적으로 `standby_req_tbl` 대기열에 등록되었습니다.
  * `400 Bad Request`: 현재 로그인된 사용자의 상태가 `pending`이 아닌 경우
  * `401 Unauthorized`: 로그인하지 않았거나 유효한 인증 정보가 없습니다.
  * `404 Not Found`: (이 경우는 내부적으로 발생할 가능성이 매우 낮지만, 만약 `current_user.id`에 해당하는 사용자를 데이터베이스에서 찾을 수 없을 때 반환될 수 있습니다.)

---

## Get My Profile (내 정보 조회)

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
  "role": 200,
  "status": "active",
  "discord_id": null,
  "discord_name": null,
  "major_id": 1,
  "profile_picture": "https://google.oauth.etc",
  "profile_picture_is_url": true,
  "last_login": "2025-05-01T09:00:00",
  "created_at": "2025-04-01T12:00:00",
  "updated_at": "2025-04-30T12:00:00"
}
```
- **Status Codes**:
  - `200 OK`
  - `401 Unauthorized` (인증 실패 시)

---

## Get Executives (임원 목록 조회)

* **Method**: `GET`
* **URL**: `/api/user/executives`
* **Description**: executive 권한 이상의 사용자를 조회한다. 임원의 id, name, role, profile_picture, profile_picture_is_url를 반환한다. 
* **Response**:

```json
[
  {
    "id": "f81d4fae7dec11d0a76500a0c91e6bf6",
    "name": "홍길동",
    "role": 500,
    "profile_picture": "https://google.oauth.etc",
    "profile_picture_is_url": true,
  }
]
```

* **Status Codes**:
    * `200 OK`

---

## Get Users (사용자 목록 조회)

* **Method**: `GET`
* **URL**: `/api/executive/users`
* **Description**: Query Parameter에 맞는 사용자를 조회한다. 
* **Query Parameters**: all optional
    * `email`: `str`
    * `name`: `str`
    * `phone`: `str`
    * `student_id`: `str`
    * `user_role`: `str`
    * `status`: `str`
    * `discord_id`: `int`: 빈 문자열을 입력하면 null을 검색한다. 
    * `discord_name`: `str`: 빈 문자열을 입력하면 null을 검색한다. 
    * `major_id`: `int`
* **Example Request**:
    * To get executives: `/api/executive/users?user_role=executive`
    * To get presidents: `/api/executive/users?user_role=president`
    * To get all users:  `/api/executive/users`
    * To get users whose discord_id is null: `/api/executive/users?discord_id=`
* **Response**:

```json
[
  {
    "id": "f81d4fae7dec11d0a76500a0c91e6bf6",
    "email": "executive@example.com",
    "name": "홍길동",
    "phone": "01012345678",
    "student_id": "202512345",
    "role": 500,
    "status": "active",
    "discord_id": null,
    "discord_name": null,
    "major_id": 1,
    "profile_picture": "https://google.oauth.etc",
    "profile_picture_is_url": true,
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

## Get User by ID(Executive)

- **Method**: `GET`  
- **URL**: `/api/executive/user/:id`  
- **설명**: ID로 사용자 조회
- **Response**:
```json
{
  "id": "b4c9a289323b21a01c3e940f150eb9b8c542587f1abfd8f0e1cc1ffc5e475514",
  "email": "user@example.com",
  "name": "홍길동",
  "phone": "01012345678",
  "student_id": "202312345",
  "role": 200,
  "status": "active",
  "discord_id": null,
  "discord_name": null,
  "major_id": 1,
  "profile_picture": "https://google.oauth.etc",
  "profile_picture_is_url": true,
  "last_login": "2025-05-01T09:00:00",
  "created_at": "2025-04-01T12:00:00",
  "updated_at": "2025-04-30T12:00:00"
}
```
- **Status Codes**:
  - `200 OK`
  - `404 Not Found` (유효하지 않은 ID)

---

## Get Role Names (각 role level의 명칭 반환)

* **Method**: `GET`
* **URL**: `/api/role_names`
* **Description**: 각 role level의 명칭을 반환한다. **만약 role name을 변경하더라도, 프론트엔드 로직과의 통일성을 위해 관리자는 500 이상, 비관리자는 500 미만의 role level을 가지고 있어야 한다.**
* **Query Parameters**: optional (defaults to English)
    * `lang`: `str`
* **Example Request**:
    * To get names in English: `/api/users?lang=en`
    * To get names in Korean: `/api/users?lang=ko`
    * If unidentified language code, defaults to English
* **Response**:

```json
{
    "role_names": {
        "0": "lowest",
        "100": "dormant",
        "200": "newcomer",
        "300": "member",
        "400": "oldboy",
        "500": "executive",
        "1000": "president"
    }
}
```
```json
{
    "role_names": {
        "0": "최저권한",
        "100": "휴회원",
        "200": "준회원",
        "300": "정회원",
        "400": "졸업생",
        "500": "운영진",
        "1000": "회장"
    }
}
```

* **Status Codes**:
    * `200 OK`
    * `401 Unauthorized`

---

## Update My Profile (내 정보 수정)

- **Method**: `POST`  
- **URL**: `/api/user/update`  
- **설명**: 로그인한 사용자의 정보 수정  
- **Request Body**:
```json
{
  "name": "김철수",
  "phone": "01056781234", 
  "student_id": "202312345", 
  "major_id": 2,
  "profile_picture": "https://google.oauth.etc",
  "profile_picture_is_url": true
}
```
- 모든 field는 optional
- 이 route로는 profile_picture을 url로만 변경할 수 있으며, file로 변경하려면 후술될 별도의 route를 사용해야 한다. 

- **Status Codes**:
  - `204 No Content`
  - `400 Bad Request` (유효하지 않은 이미지 url)
  - `401 Unauthorized`
  - `422 Unprocessable Content`


## Update My Profile Picture With File (내 프로필 사진을 파일로 변경)

- **Method**: `POST`  
- **URL**: `/api/user/update-pfp-file`  
- **설명**: 로그인한 사용자의 정보 수정  
- **Request**:
  * **Content-Type**: `multipart/form-data`
  * **Form Fields**:

    | 필드명  | 타입   | 필수 여부 | 설명                    |
    | ---- | ---- | ----- | --------------------- |
    | file | File | O   | 업로드할 파일 (png, jpg, jpeg) |

- **Status Codes**:
  - `204 No Content`
  - `401 Unauthorized`
  - `422 Unprocessable Content`

---

## Delete My Profile (휴회원으로 변경)

- **Method**: `POST`  
- **URL**: `/api/user/delete`  
- **설명**: 로그인한 사용자의 계정을 휴회원으로 변경함  

- **Status Codes**:
  - `204 No Content`
  - `401 Unauthorized`
  - `403 Forbidden` (관리자 계정은 휴회원 처리 불가 등)

---

## Login

- **Method**: `POST`  
- **URL**: `/api/user/login`  
- **설명**: 로그인
- **Request Body**:
```json
{
  "email": "user@example.com",
  "hashToken": "some-hash-token"
}
```
로그인 시 요구되는 `hashToken`은 HMAC-SHA256 hash 값으로, 생성 방법은 다음과 같다.
```py
def generate_user_hash(email: str) -> str:
    secret = get_settings().api_secret.encode()
    msg = email.lower().encode()
    return hmac.new(secret, msg, hashlib.sha256).hexdigest()
```
`x-api-secret`값을 secret으로 하고 유저의 이메일을 메시지로 하여 생성한다. `x-api-secret`을 알고 있는 신뢰할 수 있는 서버에서 생성하도록 한다.

- **Request Body**:
```json
{
  "jwt":"some-encoded-jwt"
}
```

- **Status Codes**:
  - `200 OK` (기존 유저 로그인)
  - `401 Unauthorized` (hashToken 유효하지 않음) 
  - `404 Not Found` (유효하지 않은 email)

> ⚙ `last_login`은 이 시점에서 자동 업데이트.  

---

## Change User (관리자 기능)

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



## 졸업생 전환 신청 관리 API (`/api/user/oldboy`)

- `oldboy_applicant` 테이블의 데이터를 관리하는 API입니다.
- 이 테이블은 `user` 테이블의 `id`를 참조하며, 졸업생 전환 신청자의 처리 여부와 신청/업데이트 시각을 기록합니다.

---

## Register Oldboy Applicant

- **Method**: `POST`
- **URL**: `/api/user/oldboy/register`
- **Description**: 로그인된 사용자에 대해 새로운 졸업생 전환 신청 기록을 생성합니다. 정회원이며, 사용자 생성일(user.created_at, UTC 기준)로부터 156주(3년)가 경과한 경우에만 신청할 수 있습니다.

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
  - `409 Conflict`: 이미 신청 기록이 존재하는 `id`로 신청을 시도

---

## Get Oldboy Applicant(Self)

- **Method**: `GET`
- **URL**: `/api/user/oldboy/applicant`
- **Description**: 로그인된 사용자의 졸업생 전환 신청 기록을 조회합니다. 
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
  - `200 OK`
  - `401 Unauthorized`: (로그인하지 않음)
  - `404 Not Found`: 졸업생 전환 신청 기록 없음

---

## Get All Oldboy Applicants

- **Method**: `GET`
- **URL**: `/api/executive/user/oldboy/applicants`
- **Description**: 졸업생 전환 신청 기록을 조회합니다.
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

## Process Oldboy Applicant

- **Method**: `POST`
- **URL**: `/api/executive/user/oldboy/:id/process`
- **Description**: 특정 `id`를 가진 사용자의 졸업생 전환 신청 `processed` 상태를 업데이트하고 신청자의 권한을 `oldboy`로 변경합니다. 
- **Status Codes**:
  - `204 No Content`: 업데이트 성공
  - `401 Unauthorized`: 로그인하지 않음
  - `403 Forbidden`: 권한 없음 (예: 관리자가 아님)
  - `404 Not Found`: 해당 ID의 졸업생 전환 신청 기록 없음
  - `409 Conflict`: 이미 oldboy인 사용자에 대해 요청함

---

## Unregister Oldboy Applicant(Self)

- **Method**: `POST`
- **URL**: `/api/user/oldboy/unregister`
- **Description**: 로그인한 사용자의 졸업생 전환 신청 기록이 처리되지 않았다면 삭제합니다. 
- **Status Codes**:
  - `204 No Content`: 삭제 성공
  - `401 Unauthorized`: 로그인하지 않음
  - `404 Not Found`: 해당 ID의 졸업생 전환 신청 기록 없음
  - `409 Conflict`: 신청이 이미 처리됨

---

## Unregister Oldboy Applicant(Executive)

- **Method**: `POST`
- **URL**: `/api/executive/user/oldboy/:id/unregister`
- **Description**: 특정 `id`를 가진 사용자의 졸업생 전환 신청 기록을 삭제합니다. 
- **Status Codes**:
  - `204 No Content`: 삭제 성공
  - `401 Unauthorized`: 로그인하지 않음
  - `403 Forbidden`: 권한 없음 (예: 관리자가 아님)
  - `404 Not Found`: 해당 ID의 졸업생 전환 신청 기록 없음

---

## Reactivate Oldboy Applicant(Self)

- **Method**: `POST`
- **URL**: `/api/user/oldboy/reactivate`
- **Description**: 로그인한 사용자의 권한이 `oldboy`이면 권한을 `member`로 바꾸고 상태를 `pending`으로 변경합니다. 기존 `oldboy_applicant` 기록이 삭제됩니다. 
- **Status Codes**:
  - `204 No Content`
  - `400 Bad Request`: 사용자의 권한이 `oldboy`가 아님
  - `401 Unauthorized`: 로그인하지 않음

---

## 입금 확인(standby) API (`/api/user/standby`)

- `standby`는 입금 확인을 기다리는 회원들을 관리하는 API입니다.

---

## Get Standby Request List
- **Method**: `GET`
- **URL**: `/api/executive/user/standby/list`
- **Response**:
```json
[
    {
        "deposit_name": "Alice Kim78",
        "is_checked": false,
        "user_name": "Alice Kim",
        "standby_user_id": "b36a83701f1c3191e19722d6f90274bc1b5501fe69ebf33313e440fe4b0fe210",
        "deposit_time": null
    },
    {
        "deposit_name": "Bob Lee88",
        "is_checked": true,
        "user_name": "Bob Lee",
        "standby_user_id": "15e4c3b1b3006382a22241ea66d679c107bc9b15cf8e6a25b64f46ac559c50c9",
        "deposit_time": "2025-06-01T23:33:28"
    }
]
```
- **Status Codes**:
  - `200 OK`
  - `401 Unauthorized` (로그인하지 않음)
  - `403 Forbidden` (관리자(executive) 권한 없음)

---

## Manually Process Standby Request

- **Method**: `POST`
- **URL**: `/api/executive/user/standby/process/manual`
- **Request Body**:
```json
{
  "id": "b36a83701f1c3191e19722d6f90274bc1b5501fe69ebf33313e440fe4b0fe210"
}
```

- **Status Codes**:
  - `204 No Content`: 성공
  - `401 Unauthorized` (로그인하지 않음)
  - `403 Forbidden` (관리자(executive) 권한 없음)
  - `404 Not Found` (사용자가 없음)
  - `409 Conflict` (이미 active인 사용자에 대해 요청함)

---

## Process Standby Request List with File

- **Method**: `POST`
- **URL**: `/api/executive/user/standby/process`
- **Request**:
  - **Content-Type**: `multipart/form-data`
  - **Form Fields**:

    | 필드명  | 타입   | 필수 여부 | 설명                    |
    | ---- | ---- | ----- | --------------------- |
    | file | File | O    | 업로드할 파일 (csv(UTF-8 or EUC-KR)) |

- **Status Codes**:
  - `200 OK`: 성공
  - `400 Bad Request`: 파일 누락 또는 유효하지 않은 파일 또는 기타 인코딩 문제 또는 입금 내역 오류
  - `401 Unauthorized` (로그인하지 않음)
  - `403 Forbidden` (관리자(executive) 권한 없음)
  - `409 Conflict` (중복 데이터 삽입)
  - `413 Content Too Large`: 파일 업로드 최대 크기 초과
  - `422 Unprocessable Content`: 파일 누락 또는 필드명 오류

- Request, Response에 관한 자세한 설명은 아래를 참고하시기 바랍니다

### Request

#### Request File

업로드할 파일은 다음 구조를 가져야 합니다. 

1. 5번째 줄은 "거래일시,적요,보낸분/받는분,송금메모,출금액,입금액,잔액,거래점,구분"이어야 합니다. 1~4줄은 무시합니다.
2. 6번째 줄부터 마지막 직전 줄까지 위 형식에 맞는 입금 기록이 있어야 합니다.
    - `거래일시`는 `%Y.%m.%d %H:%M:%S` 형식의 시각(예 2025.06.02 08:33:28)이어야 하고, 한국 표준시(UTC+9)을 사용해야 합니다.
    - `보낸분/받는분`에는 회원의 이름과 전화번호 끝 2자리를 합친 형식(예 홍길동12)을 권장합니다. 
    - 끝 2자리가 숫자이면 이름과 전화번호로 회원을 검색하고, 그렇지 않으면 이름으로 회원을 검색합니다. 
    - 검색 결과가 여러 건이면 해당 입금 기록은 처리되지 않습니다. 
3. 마지막 줄은 합계를 나타내는 줄이므로 무시합니다. 

### Response

요청은 다음 과정에 따라 처리됩니다. 
1. 파일의 확장자가 csv가 아니면 status code 400을 반환합니다.
2. 파일의 용량을 확인하여 최대 크기를 초과하면 status code 413을 반환합니다.
3. 파일을 읽고, 이에 실패하면 status code 400을 반환합니다.
4. 위 과정을 정상적으로 통과한다면, status code 200을 response body와 함께 반환합니다. 

#### Response Body

response body는 각 입금 기록의 처리 결과를 포함하며 자세한 내용은 다음과 같습니다. 

```json
{
    "cnt_succeeded_records": 0,
    "cnt_failed_records": 3,
    "results": [
        {
            "result_code": 412,
            "result_msg": "해당 입금 기록에 대응하는 사용자의 상태는 UserStatus.standby로 pending 상태가 아닙니다.",
            "record": {
                "amount": 300000,
                "deposit_time": "2025-06-01T23:33:28Z",
                "deposit_name": "Bob Lee"
            },
            "users": [
                {
                    "id": "15e4c3b1b3006382a22241ea66d679c107bc9b15cf8e6a25b64f46ac559c50c9",
                    "email": "exec@example.com",
                    "name": "Bob Lee",
                    "major_id": 1
                }
            ]
        },
        ...
    ]
}
```

- `cnt_succeeded_records`: 처리에 성공한 입금 기록의 개수
- `cnt_failed_records`: 처리에 실패한 입금 기록의 개수
- `results`: 입금 기록별 결과 리스트
  - `result_code`: 결과 코드
  - `result_msg`: 결과 메시지
  - `record`: 해당 입금 기록
    - `amount`: 입금액
    - `deposit_time`: 입금 시각(UTC)
    - `deposit_name`: 입금자명
  - `users`: 해당 처리 결과에 대응하는 사용자 리스트. `/api/user/:id`의 결과와 동일한 정보만 포함한다. 

입금 기록은 하나씩 순서대로 처리됩니다. 실행 과정에 따라 나열된 상황별 결과 코드 등은 다음과 같습니다. 

##### `standby_req_tbl` 테이블 중복 검색
- `standby_req_tbl` 테이블에서 `is_checked`가 `false`인 것 중 입금자명에 대응하는 것이 2개 이상인 경우
- `result_code`: 409
- `result_msg`: "해당 입금 기록에 대응하는 사용자가 입금 대기자 명단에 ?건 존재합니다"
- `users`: 해당 입금 기록에 대응하는 사용자 리스트

##### `user` 테이블 중복 검색
- `user` 테이블에 입금자명에 대응하는 것이 2개 이상인 경우
- `result_code`: 409
- `result_msg`: "해당 입금 기록에 대응하는 사용자가 사용자 테이블에 ?건 존재합니다"
- `users`: 해당 입금 기록에 대응하는 사용자들 리스트

##### `user` 테이블 검색 실패
- `user` 테이블에 입금자명에 대응하는 것이 없는 경우
- `result_code`: 404
- `result_msg`: "해당 입금 기록에 대응하는 사용자가 사용자 테이블에 존재하지 않습니다"
- `users`: `[]`

##### `user` 테이블의 사용자 상태가 pending이 아님
- `user` 테이블에 입금자명에 대응하는 것이 있지만, `status`가 `pending`이 아닌 경우
- `result_code`: 412
- `result_msg`: "해당 입금 기록에 대응하는 사용자의 상태는 ?로 pending 상태가 아닙니다"
- `users`: 해당 입금 기록에 대응하는 사용자 리스트

##### `standby_req_tbl` 데이터 추가 관련
- 이 단계까지 도달한다면 `user` 테이블에 입금자명에 대응하는 사용자가 `standby_req_tbl` 테이블에 없을 경우 해당 사용자를 enroll(`/api/user/enroll`과 동일한 효과)합니다.
- 따라서 `standby_req_tbl`에 데이터가 생성되고 사용자의 상태가 `standby`로 변경됩니다. 

##### 입금액 부족
- 입금액이 기준보다 적은 경우
- `result_code`: 402
- `result_msg`: "입금액이 {get_settings().enrollment_fee}원보다 적습니다"
- `users`: 해당 입금 기록에 대응하는 사용자 리스트

##### 입금액 과다
- 입금액이 기준보다 많은 경우
- `result_code`: 413
- `result_msg`: "입금액이 {get_settings().enrollment_fee}원보다 많습니다"
- `users`: 해당 입금 기록에 대응하는 사용자 리스트

##### 사용자 상태가 standby가 아님
- 사용자의 `status`가 `standby`이 아닌 경우
- `result_code`: 412
- `result_msg`: "해당 입금 기록에 대응하는 사용자의 상태는 ?로 standby 상태가 아닙니다"
- `users`: 해당 입금 기록에 대응하는 사용자 리스트

##### 성공
- 입금 확인 및 status 변경이 정상적으로 처리된 경우
- `result_code`: 200
- `result_msg`: "성공"
- `users`: 해당 입금 기록에 대응하는 사용자 리스트

##### 알 수 없는 오류
- 입금 확인 및 status 변경이 정상적으로 처리되지 않은 경우
- `result_code`: 500
- `result_msg`: "알 수 없는 오류: ..."
- `users`: `[]`


## Process Deposit

- **Method**: `POST`
- **URL**: `/api/executive/user/standby/process/deposit`
- **Request Body**:
```json
{
    "amount":300000,
    "deposit_time":"2025-08-17T15:23:23Z",
    "deposit_name":"Discord Bot"
}
```
- `deposit_time`은 UTC 형식을 지켜야 합니다


- **Response**:
```json
{
    "result": {
        "result_code": 412,
        "result_msg": "해당 입금 기록에 대응하는 사용자의 상태는 UserStatus.active로 pending 상태가 아닙니다",
        "record": {
            "amount": 300000,
            "deposit_time": "2025-08-17T15:23:23Z",
            "deposit_name": "Discord Bot"
        },
        "users": [
            {
                "id": "a44946fbf09c326520c2ca0a324b19100381911c9afe5af06a90b636d8f35dd5",
                "email": "bot@discord.com",
                "name": "Discord Bot",
                "major_id": 1
            }
        ]
    }
}
```
- `Process Standby Request List with File`과 동일한 과정으로 처리되며 결과가 `result` 안에 담겨 반환됩니다

- **Status Codes**:
  - `200 OK`
  - `401 Unauthorized` (로그인하지 않음)
  - `403 Forbidden` (관리자(executive) 권한 없음)

---
