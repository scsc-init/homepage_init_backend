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