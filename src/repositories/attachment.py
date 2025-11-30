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
        article_exists_stmt = select(Article.id).where(Article.id == article_id)
        if not self.session.scalar(article_exists_stmt):
            return []

        valid_file_ids_stmt = select(FileMetadata.id).where(
            FileMetadata.id.in_(file_ids)
        )
        valid_file_ids = set(self.session.scalars(valid_file_ids_stmt).all())
        data_to_insert = [
            {"article_id": article_id, "file_id": file_id} for file_id in valid_file_ids
        ]
        if not data_to_insert:
            return []

        stmt = insert(Attachment).values(data_to_insert).returning(Attachment.file_id)

        result = self.session.execute(stmt)
        return [r.tuple()[0] for r in result.all()]

    def delete_by_article_id(self, article_id: int):
        stmt = delete(Attachment).where(Attachment.article_id == article_id)
        self.session.execute(stmt)


AttachmentRepositoryDep = Annotated[AttachmentRepository, Depends()]
