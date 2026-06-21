# SCSC global status 백업 및 전환 문서

> 최초 작성일: 2026-06-21

## 1. 배경

기존에는 `scsc global status`를 변경할 때 상태 전환 로직만 수행했고, 전환 직전의 DB 스냅샷을 운영자가 별도로 남기기 어려웠다.  
이 때문에 학기 전환, SIG/PIG 아카이브 처리, 사용자 상태 갱신이 함께 일어나는 구간에서 문제가 생기면 복구 기준점이 불명확했다.

이 이슈를 해결하기 위해 다음 두 동작을 표준화했다.

1. `scsc global status` 변경 전에 DB 전체를 자동 백업한다.
2. 운영자가 필요할 때 현재 DB 상태를 수동으로 백업해 내려받을 수 있는 route를 제공한다.

## 2. 관련 API

### 2.1 현재 상태 조회

`GET /api/scsc/global/status`

- 현재 `scsc_global_status` 레코드를 반환한다.
- 상태 전환이나 백업은 수행하지 않는다.

### 2.2 상태 목록 조회

`GET /api/scsc/global/statuses`

- 허용되는 상태 목록을 반환한다.
- 현재 구현상 `recruiting`, `active` 두 값만 노출한다.

### 2.3 상태 변경

`POST /api/executive/scsc/global/status`

- 요청 본문 예시:

```json
{ "status": "active" }
```

- 상태 변경 전에 `backup_db_before_status_change()`를 먼저 실행한다.
- 백업이 실패하면 상태 변경도 중단하고 `500`을 반환한다.
- 허용되는 전환만 처리한다.
  - `recruiting -> active`
  - `active -> recruiting`

### 2.4 수동 백업 다운로드

`POST /api/executive/scsc/global/status/backup`

- 현재 DB를 백업한 뒤 생성된 `.sql` 파일을 바로 응답한다.
- 응답 타입은 `application/sql`이다.
- 파일은 서버의 `logs/db_backups` 아래에 저장된다.

## 3. 권한 정책

- 상태 조회 API는 일반 조회로 취급한다.
- 상태 변경 API와 수동 백업 API는 `president` 권한이 필요하다.
- `backup_current_db()`는 호출자 역할이 `president`보다 낮으면 `403`을 반환한다.

## 4. 백업 파일 생성 방식

백업은 `pg_dump`로 생성한다.

- DB 이름, 연도, 학기, 상태, 생성 시각을 파일명에 포함한다.
- 파일명 예시:

```text
{db_name}_{year}_{semester}_{status}_{timestamp}_before_status_change.sql
```

- 실제 저장 위치:

```text
homepage_init_backend/logs/db_backups
```

## 5. 상태 변경 시 처리 순서

`POST /api/executive/scsc/global/status`가 호출되면 아래 순서로 처리한다.

1. 현재 상태와 목표 상태가 허용된 전환인지 확인한다.
2. 현재 상태가 `active`이면 학기 전환 가능 여부를 먼저 검사한다.
3. 전환 직전 DB를 백업한다.
4. `recruiting -> active`일 때 SIG/PIG의 모집 상태를 활성화한다.
5. `active -> recruiting`일 때 아카이브, 사용자 상태, 대기열, 신청자 처리 등을 정리한다.
6. `scsc_global_status`를 새 상태로 갱신하고 커밋한다.

## 6. 운영 주의사항

- 백업 실패를 무시하고 상태를 바꾸지 않는다. 복구 기준점이 사라지기 때문이다.
- 수동 백업 route는 "현재 상태를 바로 저장"하는 용도다.
- 상태 변경 route는 "전환 전에 자동 백업 후 상태 변경"하는 용도다.
- 두 route는 목적이 다르므로 운영 시 혼동하지 않아야 한다.

