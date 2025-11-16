import csv
import hashlib
import hmac
import io
from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Request
from pydantic import BaseModel, field_validator

from src.core import get_settings
from src.db import SessionDep
from src.model import User

map_semester_name = {
    1: "1",
    2: "S",
    3: "2",
    4: "W",
}


def split_filename(filename: str) -> tuple[str, str]:
    """
    Splits a filename into its base name and extension.

    Examples:
    - 'document.pdf' -> ('document', 'pdf')
    - 'archive.tar.gz' -> ('archive.tar', 'gz')
    - 'photo' -> ('photo', '')
    - '.gitignore' -> ('.gitignore', '')

    Args:
        filename: The full name of the file (str).

    Returns:
        A tuple containing the base name (str) and the extension (str, without the dot).
    """
    parts = filename.rsplit(".", 1)

    if len(parts) == 1:
        # No dot found, so the entire filename is the base name, and the extension is empty.
        return parts[0], ""

    base_name, extension = parts

    # Special handling for filenames that start with a dot (like '.gitignore')
    # and do not have another dot. rsplit gives ('', 'gitignore').
    # If the original filename *started* with a dot, and there was only one dot found
    # (meaning the base_name is empty), we typically treat the whole thing as the base name.
    if not base_name and filename.startswith("."):
        return filename, ""

    return base_name, extension.lower()


def get_user(request: Request, session: SessionDep) -> User:
    settings = get_settings()

    if not settings.user_check:  # for development
        user = session.get(
            User,
            "12350b93cae7322f29d409e12a998a598c703780c5f00c99ddf372c38817e4f4",
        )
        if user:
            return user
        raise HTTPException(status_code=401, detail="User not found")

    encoded_jwt = request.headers.get("x-jwt")
    if encoded_jwt is None:
        raise HTTPException(status_code=401, detail="No x-jwt included")

    try:
        decoded_jwt = jwt.decode(
            encoded_jwt,
            settings.jwt_secret,
            algorithms=["HS256"],
            options={"require": ["user_id", "exp"], "verify_exp": True},
        )
    except jwt.exceptions.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Expired x-jwt")
    except jwt.exceptions.InvalidSignatureError:
        raise HTTPException(status_code=401, detail="Invalid x-jwt")
    except jwt.exceptions.MissingRequiredClaimError:
        raise HTTPException(status_code=401, detail="Missing required claim in x-jwt")
    except jwt.exceptions.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token in x-jwt")

    user = session.get(User, decoded_jwt["user_id"])
    if user:
        return user

    raise HTTPException(status_code=401, detail="User not found")


UserDep = Annotated[User, Depends(get_user)]


def kst2utc(kst_naive_dt: datetime) -> datetime:
    utc_dt = kst_naive_dt - timedelta(hours=9)
    utc_dt_aware = utc_dt.replace(tzinfo=timezone.utc)
    return utc_dt_aware


def get_new_year_semester(old_year: int, old_semester: int) -> tuple[int, int]:
    return old_year + old_semester // 4, old_semester % 4 + 1


def generate_user_hash(email: str) -> str:
    secret = get_settings().api_secret.encode()
    msg = email.lower().encode()
    return hmac.new(secret, msg, hashlib.sha256).hexdigest()


class DepositDTO(BaseModel):
    amount: int
    deposit_time: datetime  # should be utc
    deposit_name: str

    model_config = {"from_attributes": True}  # enables reading from ORM objects

    @field_validator("deposit_time")
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
    result = [
        DepositDTO(
            amount=int(str(line["입금액"]).replace(",", "")),
            deposit_time=kst2utc(
                datetime.strptime(line["거래일시"], "%Y.%m.%d %H:%M:%S")
            ),
            deposit_name=line["보낸분/받는분"],
        )
        for line in reader
    ]
    return result
