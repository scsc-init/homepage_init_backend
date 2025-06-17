# 오픈뱅킹 관련 DB, API 명세서
**최신개정일** 2025-06-18

# DB 구조

## 계좌 정보 DB
```sql
CREATE TABLE banking_account_details (
    id INT NOT NULL PRIMARY KEY DEFAULT 1,
    access_token TEXT NOT NULL,
    refresh_token TEXT NOT NULL,
    user_seq_no VARCHAR(64) NOT NULL,
    access_token_expire DATETIME NOT NULL,
    scope VARCHAR(255) NOT NULL,
    fintech_use_num VARCHAR(32),
    tran_id_tail INT,
    CONSTRAINT ck_id_valid CHECK (id = 1)
);
```
후술되는 Open API의 OAuth 기작을 통해서만 등록되며, 동아리 계좌 한 종류만 등록되어야 함.

# API 구조

## 오픈뱅킹 API 사용 관련 API(/api/bank)

- 오픈뱅킹 API를 통해 동아리 계좌를 등록하고,
- 동아리 계좌의 입금내역을 확인함.

유의사항
- 테스트 시 open api uri를 `testapi`로 사용, 실제 배포 시 `openapi`로 변경
- 개발자 사이트에서 테스트 권한이 아직 부여되지 않아 내부 로직 테스트는 아직 안됨

## 🔹 동아리 계좌 등록용 OAuth2.0 URL 생성

- **Method**: `GET`  
- **URL**: `/api/bank/auth-url`
- **설명**: oauth url 생성, 동아리 회장만 접근 가능
- **Request Body**:
None

- **Response**:
```json
{
    "auth_url": "https://testapi.openbanking.or.kr/oauth/2.0/authorize?response_type=code&client_id=...&redirect_uri=http://localhost:8080/bank/callback&scope=login%20inquiry&state=...&auth_type=0"
}
```
- **Status Codes**:
  - `200 OK`
  - `401 Unauthorized`
  - `403 Forbidden` (회장 권한 없음)


---

## 🔹 입금 확인

- **Method**: `GET`  
- **URL**: `/api/bank/inquiry`  
- **설명**: 지정된 기간 내 동아리 계좌에 입금 여부 확인
- **Request Body**:
```json
{
    "depositer": "입금자명",
    "from_date": "20250618",
    "to_date": "20250618"
}
```
- **Response**:
```json
{
  "trx_true": "true"
}
```
- **Status Codes**:
  - `200 OK`
  - `400 Bad Request` (파라미터 등 이슈로 토큰 리퀘스트 실패)
  - `401 Unauthorized` (권한 부족)
  - `404 Not Found` (등록된 동아리 계좌가 없음, 또는 토큰이 없음)

---

TODO: 테스트 권한을 발급받아 로직 구현 마무리
