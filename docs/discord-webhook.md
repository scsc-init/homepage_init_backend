# 디스코드 웹훅 기능 명세서
**최신개정일:** 2025-10-26

# 개요
- 이 레포는 Github webhook 기능을 디스코드 채널과 연동시켜 알림을 받습니다.
- 연동된 디스코드 채널은 SCSC 공식 디스코드 서버의 `scsc_init_backend-pr` 입니다.

# 설정 방법
1. 디스코드 서버 설정
    - 웹훅을 추가하고자 하는 채널 선택 > settings > Integrations > Webhooks > New Webhook
    - 웹훅 URL을 복사
2. 깃헙 레포 설정
    - settings > Webhooks > Add webhook
    - 복사한 URL을 붙여넣고 끝에 `/github` 추가
    - Content type을 application/json으로 변경
    - 적절한 트리거 이벤트 설정

# 기능

- PR 이벤트*가 발생하면 메시지가 채널로 전송됩니다.

---
(*) PR 이벤트는 다음을 의미합니다:
> Pull request assigned, auto merge disabled, auto merge enabled, closed, converted to draft, demilestoned, dequeued, edited, enqueued, labeled, locked, milestoned, opened, ready for review, reopened, review request removed, review requested, synchronized, unassigned, unlabeled, or unlocked.
