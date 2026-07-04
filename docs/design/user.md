# 회원 구조 문서

> 최초작성일: 2025-11-19  
> 최신개정일: 2026-07-04  
> 최신개정자: 이한경  
> 작성자: 이한경, [강명석](mailto:tomskang@naver.com)  

# 회원의 상태

회원 상태는 `user` 테이블의 두 플래그 변수로 관리된다.

- `is_active`: 활성 여부
- `is_banned`: 제명 여부
- 최초 가입 시 두 변수는 모두 `false`로 설정된다.

편의상 두 변수에 따른 상태를 다음 용어로 명명한다.

|is_active|is_banned|상태|
|---|---|---|
|0|0|inactive|
|0|1|banned|
|1|0|active|
|1|1|정의되지 않음|


# 회원의 권한(`role`)

- [common.md](../api/common.md)
- 총 7가지 권한이 존재한다. 권한의 서열은 나중에 나열된 항목이 높다. 
1. (0, 'lowest', '최저권한'): 가장 낮은 권한으로 `article.md`의 `board`에서 사용된다. 사용자에게 부여되지 않는다. 
1. (100, 'dormant', '휴회원'): 
1. (200, 'newcomer', '준회원'): 
1. (300, 'member', '정회원'): 
1. (400, 'oldboy', '졸업생'): 
1. (500, 'executive', '운영진'): 
1. (1000, 'president', '회장'): 가장 높은 권한으로 SIG/PIG 홍보 글이 저장되는 `board`(id==1)의 쓰기 권한에 사용된다. 

# 회원의 상태 및 권한 변경

회원의 상태와 권한은 회원가입, 입금 확인, 학기 전환, 재등록, 졸업생 전환 과정에서 변경된다.

## 회원 가입 flow

회원 가입은 새로운 사용자가 SCSC 웹페이지에 처음 가입하는 과정이다.

### 1. 구글 로그인 및 사용자 정보 입력

사용자는 구글 로그인을 통해 이메일과 프로필 사진 정보를 가져온 뒤, 회원가입 화면에서 다음 정보를 입력한다.

* 이름
* 전화번호
* 학번
* 전공
* 프로필 사진 URL
* hashToken

이때 `hashToken`은 신뢰할 수 있는 서버에서 `x-api-secret`을 secret으로 사용하여 생성한 HMAC-SHA256 hash 값이다.

### 2. 회원 생성

회원가입을 제출하면 다음 API가 호출된다.

* **Method**: `POST`
* **URL**: `/api/user/create`

이 API는 `user` 테이블에 새로운 회원을 생성한다.

회원 생성 시 기본값은 다음과 같다.

| 필드                       | 기본값                       |
| ------------------------ | ------------------------- |
| `id`                     | email의 sha256 hash        |
| `role`                   | `newcomer`(200)           |
| `is_active`              | `false`                   |
| `is_banned`              | `false`                   |
| `discord_id`             | `null`                    |
| `discord_name`           | `null`                    |
| `profile_picture`        | 구글 OAuth에서 반환된 프로필 사진 URL |
| `profile_picture_is_url` | `true`                    |
| `last_login`             | 현재 시각                     |
| `created_at`             | 현재 시각                     |
| `updated_at`             | 현재 시각                     |

따라서 회원가입 직후 사용자는 다음 상태가 된다.

* 상태: inactive
* 권한: newcomer

회원 생성이 정상적으로 완료되면 유저 활동 기록에 다음 기록이 추가된다.

* `activity_type`: `SIGNED_UP`
* `created_by`: `null`
* `detail`: 회원 생성 관련 내용

### 3. 입금 대기 상태

회원가입 직후 사용자는 아직 정식 등록이 완료된 상태가 아니다.

이 사용자는 입금 확인 대상이 되며, 입금 확인 API에서 등록 가능한 사용자로 판단될 수 있다.

입금자명은 다음 형식을 권장한다.

```text
이름 + 전화번호 뒤 2자리
```

예를 들어 이름이 `홍길동`이고 전화번호가 `01012345678`이면 입금자명은 다음과 같다.

```text
홍길동78
```

입금 확인 과정에서 필요하다면 `standby_req_tbl`에 입금 대기 기록이 생성된다.

`standby_req_tbl`의 주요 값은 다음과 같다.

| 필드                | 설명              |
| ----------------- | --------------- |
| `standby_user_id` | 입금 대기 중인 회원의 id |
| `user_name`       | 회원 이름           |
| `deposit_name`    | 입금자명            |
| `deposit_time`    | 입금 확인 시각        |
| `is_checked`      | 입금 확인 여부        |

### 4. 입금 확인

임원은 입금 내역을 확인하여 사용자의 등록을 처리한다.

입금 확인은 다음 API 중 하나로 수행한다.

#### 수동 입금 확인

* **Method**: `POST`
* **URL**: `/api/executive/user/standby/process/manual`

특정 사용자의 id를 직접 지정하여 입금 확인을 처리한다.

#### CSV 파일 기반 입금 확인

* **Method**: `POST`
* **URL**: `/api/executive/user/standby/process`

은행 거래내역 CSV 파일을 업로드하여 여러 입금 기록을 한 번에 처리한다.

#### 단일 입금 기록 처리

* **Method**: `POST`
* **URL**: `/api/executive/user/standby/process/deposit`

디스코드 봇 등 외부 시스템에서 전달한 단일 입금 기록을 처리할 때 사용한다.

입금 확인 과정에서는 다음 조건을 확인한다.

1. 입금자명에 대응하는 사용자가 존재하는지 확인한다.
2. 대응되는 사용자가 여러 명이면 처리하지 않는다.
3. 사용자가 제명되지 않았는지 확인한다.
4. 현재 등록 정책상 추가로 부여 가능한 등록 학기가 있는지 확인한다.
5. 입금액이 기준 금액과 일치하는지 확인한다.

입금 확인에 성공하면 다음 처리가 수행된다.

* 회원 상태가 inactive에서 active로 변경된다.
* 등록 정책에 따라 정해진 학기 수만큼 등록 기록이 생성된다.
* 입금 대기 기록이 처리 완료 상태로 변경된다.
* 유저 활동 기록에 등록 기록이 추가된다.

등록 완료 후 사용자는 다음 상태가 된다.

* 상태: active
* 권한: newcomer

유저 활동 기록에는 다음 기록이 추가된다.

* `activity_type`: `REGISTERED`
* `created_by`: 입금 확인을 처리한 임원 id
* `detail`: 등록 처리 관련 내용

## 재등록 flow

재등록은 기존 회원이 새로운 학기에 다시 등록하는 과정이다.

재등록 flow는 일반적으로 다음 순서로 진행된다.

```text
학기 전환 시작
-> 유저 접근권한 변경
-> 재등록
-> 유저 접근권한 상승 및 등록 기록 작성
```

### 1. 학기 전환 시작

학기 전환은 SCSC 전역 상태가 변경될 때 시작된다.

정규 학기 종료 또는 신규 모집 시작 시점에 SCSC 전역 상태가 변경되며, 이에 따라 기존 회원들의 상태가 재계산된다.

SCSC 전역 상태가 `active`에서 `inactive` 또는 `recruiting`으로 변경될 때, 회원의 다음 학기 등록 기록 여부에 따라 상태가 변경된다.

* 다음 학기 등록 기록이 있으면 active
* 다음 학기 등록 기록이 없으면 inactive

이 과정은 주로 `member` 이하 권한의 회원을 대상으로 한다.

```text
(<= member, active/inactive)
-> (*, active/inactive)
```

즉, 권한은 유지하되 다음 학기 등록 여부에 따라 활성 상태만 변경된다.

### 2. 유저 접근권한 변경

정규 학기로 전환될 때, 등록하지 않은 기존 회원은 휴회원으로 변경될 수 있다.

SCSC 전역 상태가 `active`에서 `inactive`로 변경될 때, 다음 조건에 해당하는 사용자는 휴회원이 된다.

```text
(<= member, inactive)
-> (dormant, inactive)
```

즉, 기존 정회원 이하 권한의 사용자가 다음 학기 등록 기록 없이 inactive 상태라면 권한이 `dormant`로 변경된다.

이 상태의 사용자는 기존 회원 정보는 유지되지만, 정회원으로서의 접근 권한은 제한된다.

### 3. 재등록 신청

재등록 대상자는 다시 입금을 진행한다.

사용자가 이미 `user` 테이블에 존재하므로, 최초 회원가입처럼 `/api/user/create`를 다시 호출하지 않는다.

재등록은 기존 사용자에 대한 입금 확인으로 처리된다.

임원은 입금 내역을 기준으로 다음 API 중 하나를 호출한다.

* `/api/executive/user/standby/process/manual`
* `/api/executive/user/standby/process`
* `/api/executive/user/standby/process/deposit`

입금 확인 과정은 최초 회원가입 이후 입금 확인 과정과 동일하다.

입금자명에 대응하는 기존 사용자를 찾고, 해당 사용자가 현재 등록 가능한 상태인지 확인한 뒤, 입금액이 기준 금액과 일치하면 등록을 처리한다.

### 4. 유저 접근권한 상승 및 등록 기록 작성

재등록 입금 확인에 성공하면 다음 처리가 수행된다.

* 회원 상태가 active로 변경된다.
* 등록 정책에 따라 정해진 학기 수만큼 등록 기록이 생성된다.
* 휴회원이거나 가입 기록이 있으면 권한이 정회원 권한으로 상승한다.
* 유저 활동 기록에 등록 기록이 추가된다.

예를 들어 휴회원이 재등록을 완료하면 다음과 같이 변경된다.

```text
(dormant, inactive)
-> (member, active)
```

단, 실제 권한 상승 여부와 등록 학기 수는 현재 등록 정책에 따른다.

재등록 완료 후 유저 활동 기록에는 다음 기록이 추가된다.

* `activity_type`: `REGISTERED`
* `created_by`: 입금 확인을 처리한 임원 id
* `detail`: 재등록 처리 관련 내용

## 졸업생 전환 flow

졸업생 전환은 일정 기간 이상 활동한 정회원이 졸업생 권한으로 변경되는 과정이다.

### 1. 졸업생 전환 신청

사용자는 다음 API를 통해 졸업생 전환을 신청한다.

* **Method**: `POST`
* **URL**: `/api/user/oldboy/register`

졸업생 전환 신청은 다음 조건을 만족해야 한다.

* 현재 권한이 `member`이다.
* 사용자 생성일(`user.created_at`)로부터 156주, 즉 약 3년이 경과했다.

신청이 성공하면 `oldboy_applicant` 테이블에 신청 기록이 생성된다.

신청 직후 기본값은 다음과 같다.

| 필드           | 기본값         |
| ------------ | ----------- |
| `id`         | 신청한 사용자의 id |
| `processed`  | `false`     |
| `created_at` | 현재 시각       |
| `updated_at` | 현재 시각       |

### 2. 졸업생 전환 신청 조회

사용자는 본인의 졸업생 전환 신청 기록을 조회할 수 있다.

* **Method**: `GET`
* **URL**: `/api/user/oldboy/applicant`

임원은 전체 졸업생 전환 신청 목록을 조회할 수 있다.

* **Method**: `GET`
* **URL**: `/api/executive/user/oldboy/applicants`

### 3. 임원의 졸업생 전환 승인

임원이 졸업생 전환 신청을 승인하면 다음 API가 호출된다.

* **Method**: `POST`
* **URL**: `/api/executive/user/oldboy/:id/process`

승인이 완료되면 다음 처리가 수행된다.

```text
(member, *)
-> (oldboy, *)
```

즉, 회원의 권한이 `member`에서 `oldboy`로 변경된다.

또한 졸업생 전환 신청 기록의 `processed` 값이 변경된다.

## 졸업생의 정회원 전환 flow

졸업생은 다시 정회원으로 전환할 수 있다.

졸업생이 정회원 전환을 요청하면 다음 API가 호출된다.

* **Method**: `POST`
* **URL**: `/api/user/oldboy/reactivate`

이 API는 로그인한 사용자의 권한이 `oldboy`인 경우에만 성공한다.

성공 시 다음과 같이 변경된다.

```text
(oldboy, *)
-> (member, inactive)
```

또한 기존 `oldboy_applicant` 기록은 삭제된다.

정회원으로 전환된 직후에는 inactive 상태이므로, 다시 active 상태가 되려면 재등록 flow에 따라 입금 확인 및 등록 처리가 필요하다.

## 회원 정보 변경 flow

회원 정보는 사용자 본인 또는 임원이 변경할 수 있다.

### 1. 사용자의 본인 정보 수정

사용자는 다음 API를 통해 본인 정보를 수정한다.

* **Method**: `POST`
* **URL**: `/api/user/update`

수정 가능한 필드는 다음과 같다.

* 이름
* 전화번호
* 학번
* 전공
* 프로필 사진 URL

모든 필드는 optional이며, 제공된 필드만 수정된다.

프로필 사진을 파일로 업로드하려면 다음 API를 사용한다.

* **Method**: `POST`
* **URL**: `/api/user/update-pfp-file`

### 2. 임원의 회원 정보 수정

회장은 다음 API를 통해 특정 회원 정보를 수정할 수 있다.

* **Method**: `POST`
* **URL**: `/api/executive/user/:id`

수정 가능한 주요 필드는 다음과 같다.

* 이름
* 전화번호
* 학번
* 전공
* 권한
* 활성 여부
* 제명 여부

`is_active`와 `is_banned`를 변경하려면 두 값을 모두 제공해야 한다.

또한 두 값이 동시에 `true`가 되어서는 안 된다.

## 로그인 flow

기존 사용자는 다음 API를 통해 로그인한다.

* **Method**: `POST`
* **URL**: `/api/user/login`

로그인 요청에는 다음 값이 필요하다.

* 이메일
* hashToken

로그인에 성공하면 JWT가 반환된다.

로그인 시 `last_login` 값은 자동으로 갱신된다.

단, 로그인은 회원의 상태나 권한을 변경하지 않는다.

## 회원 상태 및 권한 변경 요약

| 상황                     | 변경 전                         | 변경 후                   |
| ---------------------- | ---------------------------- | ---------------------- |
| 회원 가입                  | 없음                           | `(newcomer, inactive)` |
| 입금 확인 성공               | `(*, inactive)`              | `(*, active)`          |
| 재등록 성공                 | `(dormant/member, inactive)` | 등록 정책에 따른 권한, `active` |
| 졸업생 전환 승인              | `(member, *)`                | `(oldboy, *)`          |
| 졸업생 정회원 전환             | `(oldboy, *)`                | `(member, inactive)`   |
| 학기 변경 시 다음 학기 등록 기록 있음 | `(<= member, *)`             | `(*, active)`          |
| 학기 변경 시 다음 학기 등록 기록 없음 | `(<= member, *)`             | `(*, inactive)`        |
| 정규학기 전환 시 미등록 회원       | `(<= member, inactive)`      | `(dormant, inactive)`  |

## 관련 API 요약

| Flow             | API                                                |
| ---------------- | -------------------------------------------------- |
| 회원 생성            | `POST /api/user/create`                            |
| 로그인              | `POST /api/user/login`                             |
| 내 정보 조회          | `GET /api/user/profile`                            |
| 내 정보 수정          | `POST /api/user/update`                            |
| 프로필 사진 파일 수정     | `POST /api/user/update-pfp-file`                   |
| 임원의 회원 정보 수정     | `POST /api/executive/user/:id`                     |
| 입금 대기 목록 조회      | `GET /api/executive/user/standby/list`             |
| 수동 입금 확인         | `POST /api/executive/user/standby/process/manual`  |
| CSV 입금 확인        | `POST /api/executive/user/standby/process`         |
| 단일 입금 기록 처리      | `POST /api/executive/user/standby/process/deposit` |
| 졸업생 전환 신청        | `POST /api/user/oldboy/register`                   |
| 본인 졸업생 전환 신청 조회  | `GET /api/user/oldboy/applicant`                   |
| 전체 졸업생 전환 신청 조회  | `GET /api/executive/user/oldboy/applicants`        |
| 졸업생 전환 승인        | `POST /api/executive/user/oldboy/:id/process`      |
| 졸업생 전환 신청 취소     | `POST /api/user/oldboy/unregister`                 |
| 임원의 졸업생 전환 신청 삭제 | `POST /api/executive/user/oldboy/:id/unregister`   |
| 졸업생의 정회원 전환      | `POST /api/user/oldboy/reactivate`                 |
