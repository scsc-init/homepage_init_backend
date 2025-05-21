from datetime import datetime, timezone

from sqlmodel import CheckConstraint, Field, SQLModel

from .sig import SIGStatus


class SIGGlobalStatus(SQLModel, table=True):
    __tablename__ = "sig_global_status"  # type: ignore
    __table_args__ = (
        CheckConstraint("id = 1", name="ck_id_valid"),
    )

    id: int = Field(default=None, primary_key=True)
    status: SIGStatus = Field(default=None, nullable=False)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
