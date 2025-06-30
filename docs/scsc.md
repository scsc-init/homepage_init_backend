# SCSC 전역 상태 관련 DB, API 명세서
**최신개정일:** 2025-06-21

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
  "statuses": [ "surveying", "recruiting", "active", "inactive" ]
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
status는 ('surveying', 'recruiting', 'active', 'inactive') 중 하나
* **유효한 status 변경 방법**

|기존 status|변경 status|
|---|---|
|inactive|surveying|
|surveying|recruiting|
|recruiting|active|
|active|surveying|
|active|inactive|

* **Status Codes**:

  * `204 No Content` - 상태 변경 성공
  * `400 Bad Request` - 유효하지 않은 `status` 변경
  * `401 Unauthorized` - 인증 실패
  * `403 Forbidden` - 권한 없음 (임원이 아닌 경우)

---
