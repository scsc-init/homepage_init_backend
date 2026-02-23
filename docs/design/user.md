# 회원 구조 문서

> 최초작성일: 2025-11-19  
> 최신개정일: 2026-02-20  
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

- 회원 가입 시
  * 상태: inactive
  * 권한: newcomer
- 입금 확인 시
  * 상태: inactive -> active
  * 정해진 학기 수만큼 등록 기록을 생성
- 임원의 회원 졸업생 전환 신청 승인 시
  * 권한: member -> oldboy
  * 졸업생 전환 신청은 가입 후 156주(3년)이 지난 정회원이 할 수 있다
- 졸업생이 정회원 전환 시
  * (oldboy, *) -> (member, inactive)
- SCSC 전역 상태가 active -> inactive/recruiting 변경 시(학기 변경 시)
  * (active, <=member) -> (active/inactive, *)
  * 다음 학기 등록 기록이 있으면 active, 그렇지 않으면 inactive로 변경
- SCSC 전역 상태가 active -> inactive(정규학기로 변경 시)
  * (inactive, <=member) -> (inactive, dormant)
  * 모든 졸업생 전환 신청 승인
