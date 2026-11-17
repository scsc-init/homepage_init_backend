# SCSC 전역 상태 관련 DB, API 명세서
**최신개정일:** 2026-10-05

# DB 구조
[./common.md](./common.md) 참고


# API 구조

## SCSC 관련 API(/api/scsc)

- SCSC 전역 상태 정보를 관리하는 API

## Get Global SCSC Status

* **Method**: `GET`
* **URL**: `/api/scsc/global/status`

* **Response Body**:

```json
{
  "status": "inactive",
  "semester": 2,
  "id": 1,
  "updated_at": "2025-06-20T18:09:57",
  "year": 2025
}
```

* **Status Codes**:
  * `200 OK`

---

## Get Global SCSC Status(All Possible Statuses)

* **Method**: `GET`
* **URL**: `/api/scsc/global/statuses`

* **Response Body**:

```json
{
  "statuses": ["recruiting", "active", "inactive"]
}
```

* **Status Codes**:
  * `200 OK`

---

## Update Global SCSC Status

* **Method**: `POST`
* **URL**: `/api/executive/scsc/global/status`
* **설명**: 임원이 전체 SCSC의 상태를 일괄적으로 설정합니다

* **Request Body**:

```json
{
  "status": "active"
}
```
status는 ('recruiting', 'active', 'inactive') 중 하나
* **유효한 status 변경 방법**

|기존 status|변경 status|
|---|---|
|inactive|recruiting|
|recruiting|active|
|active|recruiting|
|active|inactive|

* **Status Codes**:

  * `204 No Content` - 상태 변경 성공
  * `400 Bad Request` - 유효하지 않은 `status` 변경
  * `401 Unauthorized` - 인증 실패
  * `403 Forbidden` - 권한 없음 (임원이 아닌 경우)
  * `412 Precondition Failed` - 등록 정책이 유효하지 않게 될 예정인 경우

---

## Backup Current SCSC DB

* **Method**: `POST`
* **URL**: `/api/executive/scsc/global/status/backup`
* **설명**: 현재 DB 상태(`pg_dump` SQL)와 `static` 폴더를 함께 `.tar.gz` 파일로 백업한 뒤 내려받습니다.

* **Status Codes**:
  * `200 OK` - 백업 파일 다운로드 성공
  * `401 Unauthorized` - 인증 실패
  * `403 Forbidden` - 권한 없음 (`president` 권한 필요)
  * `500 Internal Server Error` - DB 백업 실패

* **응답 형식**:

```http
Content-Type: application/gzip
```

* **백업 파일 위치**:
  * 서버 내부 `logs/db_backups` 디렉터리에 생성됩니다.
  * 파일명에는 DB 이름, 연도, 학기, 상태, 생성 시각이 포함됩니다.

* **백업 파일 구성**:
  * `db.sql` - `pg_dump` 결과 (`--no-owner --clean --if-exists`)
  * `static/` - 업로드된 파일 폴더

* **백업 적용 방법**: 프로젝트 루트에서 `./script/restore_backup.sh <백업파일.tar.gz>`를 실행합니다.

---
