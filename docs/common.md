# API 구조

## 공통

모든 경로에는 header에 x-api-secret을 포함해야 함

```http
x-api-secret: YOUR_SECRET_KEY
```

- **Status Codes**:
  - `401 Unauthorized` (인증 실패 시)

# SQL 관련

## 외래키 사용 설정

```sql
PRAGMA foreign_keys = ON;
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
