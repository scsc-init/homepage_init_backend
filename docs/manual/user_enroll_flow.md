# 신규 회원 가입 및 회비 납부 절차

> 최신개정일: 2025-11-18  

## 1. 개요

> 백엔드 DB의 구조는 `user.md` 참고
회원은 아래의 규칙으로 처리함.

1. **입금이 완료되지 않은 회원도 회원으로 간주**하고 준회원 상태에서 사이트 이용 가능
2. 입금 여부는 **임원진이 나중에 처리**하며, 입금 확인 후 정회원으로 전환
3. 다음 학기에 회비를 미납부한 경우 휴회원 처리
4. OB, 관리자 역할은 관리자가 관리자 페이지에서 부여


## 2. 용어 및 상태 정의

### 2.1 UserStatus

백엔드 `src/model/user.py` 기준, 회원 상태는 다음 Enum으로 관리된다.

- `active` – 회비 납부 완료된 정상 회원  
- `standby` – 회비 납부 대기 상태이지만 회원으로 취급  
- `pending` – 과거 플로우에서 사용하던 중간 상태  
- `banned` – 차단된 사용자

### 2.2 UserRole

- `newcomer` (기본 가입자)
- `member`
- `oldboy`
- `executive`
- `president`

신규 가입 시 기본값:
- `role = newcomer`
- `status = standby`

## 3. 회원가입 플로우

### 3.1 Google 로그인
Google OAuth로 로그인하여 session 확보.

### 3.2 회원가입 페이지 진입
백엔드 로그인(/api/user/login) 테스트 후:
- 가입 회원: 바로 `/` 이동  
- 신규 회원: 가입 폼(AuthClient) 렌더링

### 3.3 AuthClient 단계별 입력
1단계: 기본정보(스누메일/이름)  
2단계: 학번  
3단계: 전화번호  
4단계: 전공 선택 + 약관 동의  

### 3.4 /api/user/create
프론트에서 제출 → 백엔드가 신규 사용자 생성:
- status = standby
- role = newcomer

### 3.5 /api/auth/login
가입 직후 자동 로그인 및 `/about/welcome` 이동.

## 4. 회비 납부 절차 (사용자)

사용자는 welcome 페이지의 지정된 계좌로 회비 송금.  
입금자명 규칙: `이름+전화번호 뒤2자리`.  
회비를 납부하지 않은 경우, 로그인할 때마다 welcome페이지로 이동됨.

## 5. 입금 확인 및 처리 (임원진)

### 5.1 CSV 준비
은행 사이트에서 거래내역 다운로드 → CSV 저장.

### 5.2 자동 처리
CSV 업로드 시:
- StandbyReqTbl 기반 매칭  
- user 기반 2차 매칭  
- 금액 검증  
- 성공 시 user.status = active로 자동 전환됨

### 5.3 수동 처리
StandbyReqTbl 또는 user 기반으로 active로 승급.

## 6. 접근 제어
standby 또는 active 유저는 SIG/PIG 가입, 게시판 이용이 가능해짐

## 7. 기존 회원 처리
임원진이 OB로 전환한 사용자는 `oldboy` 역할을 부여받고, `active` 상태로 유지됨.
그 외의 기존 유저는 모두 `pending`으로 전환, 입금 확인 후에 `active` 상태로 전환됨.

## 8. 전체 흐름 요약

1. Google 로그인  
2. 백엔드 가입 여부 확인  
3. 신규는 AuthClient에서 정보 입력  
4. create_user → standby 상태로 가입  
5. 자동 로그인  
6. 입금은 나중에 임원진이 처리  
7. 입금 확인 후 active로 승격
