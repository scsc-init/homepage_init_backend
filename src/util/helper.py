import csv
import io
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, Request
from pydantic import field_validator, BaseModel
from sqlmodel import select
from typing import Type
import logging

from src.model import User, SIG, PIG, SCSCStatus, SCSCGlobalStatus
from src.db import SessionDep
from src.util.rabbitmq import send_discord_bot_request_no_reply

logger = logging.getLogger("app")

map_semester_name = {
    1: '1',
    2: 'S',
    3: '2',
    4: 'W',
}


def get_file_extension(filename: str) -> str:
    return filename.split('.')[-1].lower()


def get_user(request: Request) -> User:
    user = request.state.user
    if not user: raise HTTPException(401, detail="Not logged in")
    return user


def kst2utc(kst_naive_dt: datetime) -> datetime:
    utc_dt = kst_naive_dt - timedelta(hours=9)
    utc_dt_aware = utc_dt.replace(tzinfo=timezone.utc)
    return utc_dt_aware

def get_new_year_semester(old_year: int, old_semester: int) -> tuple[int, int]:
    return old_year + old_semester // 4, old_semester % 4 + 1


class DepositDTO(BaseModel):
    amount: int
    deposit_time: datetime  # should be utc
    deposit_name: str

    model_config = {
        "from_attributes": True  # enables reading from ORM objects
    }

    @field_validator('deposit_time')
    @classmethod
    def must_be_utc(cls, v):
        if v.tzinfo != timezone.utc:
            raise ValueError("deposit_time must be in UTC")
        return v


async def process_standby_user(encoding: str, content: bytes) -> list[DepositDTO]:
    decoded = content.decode(encoding)
    f = io.StringIO(decoded)
    lines = f.readlines()
    trimmed_lines = lines[4:-1]
    trimmed_csv = io.StringIO("".join(trimmed_lines))
    reader = csv.DictReader(trimmed_csv)
    result = [DepositDTO(
        amount=int(str(line["입금액"]).replace(',', '')),
        deposit_time=kst2utc(datetime.strptime(line["거래일시"], "%Y.%m.%d %H:%M:%S")),
        deposit_name=line["보낸분/받는분"]
    ) for line in reader]
    return result


async def process_igs(session: SessionDep, model: Type[SIG | PIG], scsc_global_status: SCSCGlobalStatus):
    action_code, name_key = (4002, 'sig_name') if model==SIG else (4004, 'pig_name')
    igs = session.exec(
        select(model).where(
            model.year == scsc_global_status.year,
            model.semester == scsc_global_status.semester,
            model.status != SCSCStatus.inactive,
        )
    ).all()

    for ig in igs:
        try:
            if ig.should_extend:
                ig.year, ig.semester = get_new_year_semester(scsc_global_status.year, scsc_global_status.semester)
                ig.status = SCSCStatus.recruiting
                session.add(ig)
            else:
                ig.status = SCSCStatus.inactive
                session.add(ig)
                await send_discord_bot_request_no_reply(action_code=action_code, body={name_key: ig.title, "previous_semester": f"{scsc_global_status.year}-{map_semester_name.get(scsc_global_status.semester)}"})
        except Exception as e:
            logger.error(f'err_type=process_igs ; ig_id={ig.id} ; ig_title={ig.title} ; msg=error processing {model.__name__}: {e}', exc_info=True)


