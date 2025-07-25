import csv
import io
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, Request
from sqlmodel import select

from src.model import User


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


@dataclass
class DepositDTO:
    amount: int
    deposit_time: datetime  # should be utc
    deposit_name: str


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

