# 회원 구조 문서

> 최초작성일: 2025-11-19  
> 최신개정일: 2025-11-24  
> 최신개정자: [강명석](mailto:tomskang@naver.com)  
> 작성자: 이한경  

# 회원의 상태(`status`)

- 'active': 활성 회원
- 'standby': 입금 확인이 완료되지 않은 회원
- 'banned': 차단된 회원
- 'pending': 사용되지 않음

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
    * 상태: standby
    * 권한: newcomer
- 입금 확인 시
    * 상태: standby -> active
- 임원의 회원 졸업생 전환 신청 승인 시
    * 권한: member -> oldboy
    * 졸업생 전환 신청은 가입 후 156주(3년)이 지난 정회원이 할 수 있다
- 졸업생이 정회원 전환 시
    * (oldboy, *) -> (member, pending)
- SCSC 전역 상태가 inactive -> recruiting 변경 시(정규학기 시작 시)
    * (pending, newcomer) -> (banned, newcomer)
    * (pending, member) & 가입 후 104주(2년) 경과 -> (banned, newcomer)
    * (pending, member) & 가입 후 104주(2년) 경과하지 않음 -> (pending, dormant)
- SCSC 전역 상태가 active -> inactive(계절학기 종료 시)
    * (active, newcomer) -> (pending, newcomer)
    * (active, member) -> (pending, member)
    * 모든 졸업생 전환 신청 승인
 
# 회원의 상태 및 권한 변경 개편안

#### 최초 회원 가입 시
- (standby, newcomer)   
#### 입금 확인 된 모든 standby 유저
- (standby, *) -> (active, *)
#### SCSC 전역 상태 active -> inactive (계절학기 종료 시)
- (active, *<president) -> (standby, *) (president 는 그냥 놔둠)
#### SCSC 전역 상태 inactive -> recruiting
- (standby, *) -> (pending, *)
- (pending, *) & (104주 경과) -> (banned, *)
