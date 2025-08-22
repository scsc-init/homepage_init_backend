# 백엔드 공통 DB, API 명세서
**최신개정일:** 2025-06-28

# API 구조

## 공통

### 인증 관련

- 모든 경로에는 header에 `x-api-secret`을 포함해야 한다. 
- `APISecretMiddleware`가 이를 처리한다. 

```http
x-api-secret: YOUR_SECRET_KEY
```

- **Status Codes**:
  - `401 Unauthorized` (인증 실패 시)

### 로그인 관련

- 사용자 정보가 필요한 경로에는 header에 `x-jwt`를 포함해야 한다. 이 값은 `/api/user/login`의 응답에서 얻는다. 
- `UserAuthMiddleware`가 이를 처리한다. 


```http
x-jwt: USER_JWT
```

- **Status Codes**:
  - `401 Unauthorized` (인증 실패 시)

### 접속 차단 관련

- `check_user_status_rule`에 등록된 `status`와 경로에 대해 해당 `status`의 사용자가 해당 경로로 요청을 보내는 것을 차단한다. 
- `CheckUserStatusMiddleware`가 이를 처리한다.
- 해당 경로에 로그인하지 않은 상태로 요청하면 401 상태 코드를, 규칙에 의해 요청이 차단되면 403 상태 코드를 반환한다. 

```sql
CREATE TABLE check_user_status_rule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_status TEXT NOT NULL CHECK (user_status IN ('active', 'pending', 'standby', 'banned')),
    method TEXT NOT NULL CHECK (method IN ('GET', 'POST')),
    path TEXT NOT NULL,
    UNIQUE (user_status, method, path)
);
```

## 코딩 스타일

### 라우터 함수 매개변수 순서
라우터 함수의 매개변수는 path parameter -> dependency(`SessionDep`, `SCSCGlobalStatusDep`, etc.) -> request -> query parameter -> body -> form data 순으로 작성한다. 

### 컨트롤러 함수 매개변수 순서
컨트롤러 함수의 매개변수는 session을 맨 앞에 작성한다. 

### `.env` 로딩
`/src/core/config.py`에서 `.env`의 변수를 지정하고 `get_settings`를 통해 다른 코드에서 불러온다. 

# SQL 관련

## 외래키 사용 설정

```sql
PRAGMA foreign_keys = ON;
```

## 테이블 생성
db 파일이 없을 때 `/docker-compose.yml`에 작성된 명령어에 따라 `/script/init_db.sh`, `/script/insert_user_roles.sh`, `/script/insert_majors.sh`를 순차적으로 실행하여 db 파일을 초기화한다. 모든 테이블은 `/script/init_db.sh`에서 생성되어야 한다. 

## 권한 DB
```sql
CREATE TABLE user_role (
    level INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    kor_name TEXT NOT NULL UNIQUE
);
```
다음의 라우터에서 사용된다
- [./user.md](./user.md) 및 user의 권한을 사용하는 부분
- [./article.md](./article.md)
- 라우터에서 권한을 query, body에 포함한다면 권한의 `name`을 입력한다. 유효하지 않은 `name`을 전달하면 400 상태 코드를 반환한다. 

다음의 권한이 존재한다. 권한에 대한 CRUD 기능은 존재하지 않고 DB 초기화 시 [./script/insert_user_roles.sh](./script/insert_user_roles.sh)에서 권한을 추가한다. 
- 총 7가지 권한이 존재한다. 권한의 서열은 나중에 나열된 항목이 높다. 
1. (0, 'lowest', '최저권한'): 가장 낮은 권한으로 `article.md`의 `board`에서 사용된다. 사용자에게 부여되지 않는다. 
1. (100, 'dormant', '휴회원'): 
1. (200, 'newcomer', '준회원'): 
1. (300, 'member', '정회원'): 
1. (400, 'oldboy', '졸업생'): 
1. (500, 'executive', '운영진'): 
1. (1000, 'president', '회장'): 가장 높은 권한으로 SIG/PIG 홍보 글이 저장되는 `board`(id==1)의 쓰기 권한에 사용된다. 


## SCSC 전역 상태 DB
```sql
CREATE TABLE scsc_global_status (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    status TEXT NOT NULL CHECK (status IN ('surveying', 'recruiting', 'active', 'inactive')),
    year INTEGER NOT NULL CHECK (year >= 2025),
    semester INTEGER NOT NULL CHECK (semester IN (1, 2, 3, 4)),

    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```
- semester의 각 값의 의미는 다음과 같다.
    * 1: 1학기 정규학기
    * 2: 여름 계절학기
    * 3: 2학기 정규학기
    * 4: 겨울 계절학기
- DB 초기화 시 `script/insert_scsc_global_status.sh` 파일의 값으로 scsc global status가 초기화된다. 

## SQL 관련
```sql
CREATE TRIGGER update_scsc_global_status_updated_at
AFTER UPDATE ON scsc_global_status
FOR EACH ROW
WHEN 
    OLD.status != NEW.status
    OLD.year != NEW.year
    OLD.semester != NEW.semester
BEGIN
    UPDATE scsc_global_status
    SET updated_at = CURRENT_TIMESTAMP
    WHERE id = OLD.id;
END;
```

## 게시판(Board) DB
총 5종류의 게시판을 초기화하며, 각 게시판의 쓰기/읽기 권한을 반영하여 아래와 같이 설정한다.

```sql
INSERT INTO board (id, name, description, writing_permission_level, reading_permission_level) VALUES (1, 'Sig', 'sig advertising board', 1000, 0);
INSERT INTO board (id, name, description, writing_permission_level, reading_permission_level) VALUES (2, 'Pig', 'pig advertising board', 1000, 0);
INSERT INTO board (id, name, description, writing_permission_level, reading_permission_level) VALUES (3, 'Project Archive', 'archive of various projects held in the club', 300, 0);
INSERT INTO board (id, name, description, writing_permission_level, reading_permission_level) VALUES (4, 'Album', 'photos of club members and activities', 500, 0);
INSERT INTO board (id, name, description, writing_permission_level, reading_permission_level) VALUES (5, 'Notice', 'notices from club executive', 500, 100);
INSERT INTO board (id, name, description, writing_permission_level, reading_permission_level) VALUES (6, 'Grant', 'applications for sig/pig grant', 200, 500);
```


## 파일 메타데이터 DB
다음의 라우터에서 사용된다
- [./image.md](./image.md)
- [./file.md](./file.md)

```sql
CREATE TABLE file_metadata (
    id TEXT PRIMARY KEY,
    original_filename TEXT NOT NULL,
    size INT NOT NULL,
    mime_type TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    owner TEXT,
    FOREIGN KEY (owner) REFERENCES user(id) ON DELETE SET NULL
);
```
- id는 uuid v4를 사용한다
- owner가 user 테이블에서 삭제되면 owner를 NULL로 바꾼다
- 파일 최대 크기와 파일 저장 경로는 `.env`를 통해 설정된다.

### 논의점
- 파일 최대 크기를 얼마로 할지 정해야 함


### SQL 관련
```sql
CREATE INDEX idx_file_metadata_owner ON file_metadata(owner);
```
