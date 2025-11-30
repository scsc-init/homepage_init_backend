from typing import Annotated

from fastapi import Depends
from sqlalchemy import delete, insert, select

from src.model import Article, Attachment, FileMetadata

from .dao import CRUDRepository


class AttachmentRepository(CRUDRepository[Attachment, int]):
    @property
    def model(self) -> type[Attachment]:
        return Attachment

    def select_by_article_id(self, article_id: int):
        stmt = select(Attachment).where(Attachment.article_id == article_id)
        return self.session.scalars(stmt).all()

    def insert_or_ignore_list(self, article_id: int, file_ids: list[str]) -> list[str]:
        with self.transaction:
            article_exists_stmt = select(Article.id).where(Article.id == article_id)
            if not self.session.scalar(article_exists_stmt):
                return []

            valid_file_ids_stmt = select(FileMetadata.id).where(
                FileMetadata.id.in_(file_ids)
            )
            db_file_ids = self.session.scalars(valid_file_ids_stmt).all()
            # Preserve order while removing duplicates
            seen: set[str] = set()
            data_to_insert: list[dict] = []
            for fid in db_file_ids:
                if fid not in seen:
                    seen.add(fid)
                    data_to_insert.append({"article_id": article_id, "file_id": fid})
            if not data_to_insert:
                return []

            stmt = (
                insert(Attachment)
                .values(data_to_insert)
                .prefix_with("OR IGNORE", dialect="sqlite")
                .returning(Attachment.file_id)
            )

            result = self.session.execute(stmt).all()
            return [r.tuple()[0] for r in result]
        return []

    def delete_by_article_id(self, article_id: int):
        with self.transaction:
            stmt = delete(Attachment).where(Attachment.article_id == article_id)
            self.session.execute(stmt)


AttachmentRepositoryDep = Annotated[AttachmentRepository, Depends()]
