from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Attachment(Base):
    __tablename__ = "attachment"
    __table_args__ = (
        UniqueConstraint("article_id", "file_id", name="uq_article_id_file_id"),
    )

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, init=False
    )
    article_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("article.id"), nullable=False
    )
    file_id: Mapped[str] = mapped_column(
        String, ForeignKey("file_metadata.id"), nullable=False
    )
