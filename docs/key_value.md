# Key-Value 설정 DB & API 가이드
**최신개정일:** 2025-10-07

## DB 구조

##key-value DB
```sql
CREATE TABLE key_value (
    key TEXT PRIMARY KEY,
    value TEXT,
    writing_permission_level INTEGER NOT NULL
        REFERENCES user_role(level) ON DELETE RESTRICT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```
### SQL관련

```sql
CREATE TRIGGER key_value_updated_at
AFTER UPDATE OF value ON key_value
FOR EACH ROW
WHEN NEW.updated_at = OLD.updated_at
BEGIN
    UPDATE key_value
    SET updated_at = CURRENT_TIMESTAMP
    WHERE key = NEW.key;
END;
```

## API 구조

##key-value 관련 API(/api/kv)

- uniquely existed value, runtime-modifiable config value 등 key-value를 필요로 하는 값들을 관리하는 API

###현재 등록된 key-value

- key:footer-message, value:서울대학교 컴퓨터 연구회\n회장 한성재 010-5583-1811\nscsc.snu@gmail.com
- key:leaders, value: null(회장, 부회장)

---

### GET key-value

- **Method**: `GET`
- **URL**: `/api/kv/{key}`
- **Response 예시**:
  ```json
  {
    "key": "footer-message",
    "value": "서울대학교 컴퓨터 연구회\n회장 한성재 010-5583-1811\nscsc.snu@gmail.com"
  }
  ```
- **Status Codes**:
  - `200 OK`
  - `404 Not Found`: 존재하지 않는 키

### post 
- **Method**: `POST`
- **URL**: `/api/kv/{key}/update`
- **Request Body**:
  ```json
  {
    "value": "새로운 값"
  }
  ```
- **Status Codes**:
  - `200 OK`
  - `401/403`: 인증 실패 또는 권한 부족
  - `404 Not Found`: 존재하지 않는 키
