# SCSC 전역 상태 변경 로직 문서

> 최초작성일: 2026-02-20  
> 최신개정일: 2026-02-20  
> 최신개정자: 이한경  
> 작성자: 이한경  

# 상태 변경 흐름

* **유효한 status 변경 방법**

|기존 status|변경 status|
|---|---|
|inactive|recruiting|
|recruiting|active|
|active|recruiting|
|active|inactive|

1학기 inactive -> 1학기 recruiting -> 1학기 active -> 여름학기 recruiting -> 여름학기 active -> 2학기 inactive -> ...

# 상황별 실행 사항

## recruiting 시작 시 (정규학기 inactive -> recruiting, 정규학기 active -> 계절학기 recruiting)

- 디스코드 봇의 시그, 피그 아카이브 카테고리 갱신

## active 시작 시 (정규, 계절학기 recruiting -> active)
- 시그, 피그의 상태를 recruiting에서 active로 변경

## active 종료 시 (학기 변경; 정규학기 active -> 계절학기 recruiting, 계절학기 active -> 정규학기 inactive)
- 요청 처리 전, 현재 등록 정책을 확인하여 부여할 마지막 학기가 현재 또는 과거의 학기라면 전역 상태 변경 요청을 거부
- 디스코드 봇 학기 변경, 아카이브 카테고리 갱신
- 모든 활성 시그, 피그에 대해:
  - should_extend이면 상태를 recruiting으로, 학기를 다음 학기로 변경
  - 아니면 상태를 inactive로 변경, 디스코드 채널을 아카이브 카테고리로 이동
- 모든 제명되지 않고 권한이 정회원 이하인 사용자에 대해:
  - 다음 학기 등록 기록이 있으면 상태를 활성으로, 그렇지 않으면 상태를 비활성으로 변경
- 입금 확인 대기 목록 초기화

## inactive 시작 시(정규학기로 변경; 계절학기 active -> 정규학기 inactive)
- 졸업생 신청 처리
- inactive이고 권한이 정회원 이하인 사용자의 권한을 휴회원으로 변경
