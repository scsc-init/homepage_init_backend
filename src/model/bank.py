from datetime import datetime, timezone

from sqlmodel import CheckConstraint, Field, SQLModel
from typing import Optional


class BankingAccountDetails(SQLModel, table=True):
    __tablename__ = "banking_account_details"  # type: ignore
    __table_args__ = (
        CheckConstraint("id = 1", name="ck_id_valid"),
    )

    id: int = Field(default=1, nullable=False, primary_key=True)
    access_token: str = Field(nullable=False)
    refresh_token: str = Field(nullable=False)
    user_seq_no: str = Field(nullable=False)
    access_token_expire: datetime = Field(nullable=False)
    scope: str = Field(nullable=False)
    fintech_use_num: Optional[str] = Field(default=None)
    tran_id_tail: Optional[int] = Field(default=None)