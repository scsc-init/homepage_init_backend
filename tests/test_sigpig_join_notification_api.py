from sqlalchemy import select

from src.model import (
    Article,
    Board,
    PIG,
    PIGMember,
    SCSCStatus,
    SIG,
    SIGMember,
)
from src.model.pig import RollingAdmission


def _create_sig_for_join(db_session, *, owner_id: str, title: str = "Algo SIG") -> SIG:
    board = Board(
        name="SIG Board",
        description="SIG content board",
        writing_permission_level=0,
        reading_permission_level=0,
    )
    db_session.add(board)
    db_session.flush()

    article = Article(title=f"{title} article", author_id=owner_id, board_id=board.id)
    db_session.add(article)
    db_session.flush()

    sig = SIG(
        title=title,
        description="SIG description",
        content_id=article.id,
        status=SCSCStatus.recruiting,
        created_year=2026,
        created_semester=1,
        year=2026,
        semester=1,
        owner=owner_id,
        is_rolling_admission=False,
    )
    db_session.add(sig)
    db_session.commit()
    db_session.refresh(sig)
    return sig


def _create_pig_for_join(db_session, *, owner_id: str, title: str = "Web PIG") -> PIG:
    board = Board(
        name="PIG Board",
        description="PIG content board",
        writing_permission_level=0,
        reading_permission_level=0,
    )
    db_session.add(board)
    db_session.flush()

    article = Article(title=f"{title} article", author_id=owner_id, board_id=board.id)
    db_session.add(article)
    db_session.flush()

    pig = PIG(
        title=title,
        description="PIG description",
        content_id=article.id,
        status=SCSCStatus.recruiting,
        created_year=2026,
        created_semester=1,
        year=2026,
        semester=1,
        owner=owner_id,
        is_rolling_admission=RollingAdmission.DURING_RECRUITING,
    )
    db_session.add(pig)
    db_session.commit()
    db_session.refresh(pig)
    return pig


def test_join_sig_sends_owner_sms_notification(
    api_client,
    build_headers,
    create_user,
    db_session,
    monkeypatch,
):
    """SIG 가입 시 시그장 번호로 문자 요청이 큐에 올라가는지 검증한다."""
    owner, _ = create_user()
    applicant, applicant_token = create_user()
    sig = _create_sig_for_join(db_session, owner_id=owner.id)

    calls = []

    async def fake_send_sms(*, to: str, content: str):
        calls.append({"to": to, "content": content})

    monkeypatch.setattr(
        "src.services.join_notification.send_sms", fake_send_sms
    )

    response = api_client.post(
        f"/api/sig/{sig.id}/member/join",
        headers=build_headers(applicant_token),
    )

    assert response.status_code == 204
    assert len(calls) == 1
    body = calls[0]
    assert body["to"] == owner.phone
    assert applicant.id in body["content"]
    assert sig.title in body["content"]


def test_join_pig_sends_owner_sms_notification(
    api_client,
    build_headers,
    create_user,
    db_session,
    monkeypatch,
):
    """PIG 가입 시 피그장 번호로 문자 요청이 큐에 올라가는지 검증한다."""
    owner, _ = create_user()
    applicant, applicant_token = create_user()
    pig = _create_pig_for_join(db_session, owner_id=owner.id)

    calls = []

    async def fake_send_sms(*, to: str, content: str):
        calls.append({"to": to, "content": content})

    monkeypatch.setattr(
        "src.services.join_notification.send_sms", fake_send_sms
    )

    response = api_client.post(
        f"/api/pig/{pig.id}/member/join",
        headers=build_headers(applicant_token),
    )

    assert response.status_code == 204
    assert len(calls) == 1
    body = calls[0]
    assert body["to"] == owner.phone
    assert applicant.id in body["content"]
    assert pig.title in body["content"]


def test_join_sig_keeps_success_even_when_sms_send_fails(
    api_client,
    build_headers,
    create_user,
    db_session,
    monkeypatch,
):
    """문자 발송 실패가 발생해도 가입 자체는 성공으로 유지되는지 확인한다."""
    owner, _ = create_user()
    applicant, applicant_token = create_user()
    sig = _create_sig_for_join(db_session, owner_id=owner.id)

    async def failing_send_sms(*, to: str, content: str):
        raise RuntimeError("mq unavailable")

    monkeypatch.setattr(
        "src.services.join_notification.send_sms", failing_send_sms
    )

    response = api_client.post(
        f"/api/sig/{sig.id}/member/join",
        headers=build_headers(applicant_token),
    )

    assert response.status_code == 204
    joined_member = db_session.scalar(
        select(SIGMember).where(SIGMember.ig_id == sig.id, SIGMember.user_id == applicant.id)
    )
    assert joined_member is not None


def test_join_pig_keeps_success_even_when_sms_send_fails(
    api_client,
    build_headers,
    create_user,
    db_session,
    monkeypatch,
):
    """문자 발송 실패가 발생해도 피그 가입은 성공하는지 확인한다."""
    owner, _ = create_user()
    applicant, applicant_token = create_user()
    pig = _create_pig_for_join(db_session, owner_id=owner.id)

    async def failing_send_sms(*, to: str, content: str):
        raise RuntimeError("mq unavailable")

    monkeypatch.setattr(
        "src.services.join_notification.send_sms", failing_send_sms
    )

    response = api_client.post(
        f"/api/pig/{pig.id}/member/join",
        headers=build_headers(applicant_token),
    )

    assert response.status_code == 204
    joined_member = db_session.scalar(
        select(PIGMember).where(PIGMember.ig_id == pig.id, PIGMember.user_id == applicant.id)
    )
    assert joined_member is not None
