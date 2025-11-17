from src.db import SessionDep, TransactionDep
from src.model import Article

from .dao import DAO


class ArticleRepository(DAO[Article, int]):
    def __init__(self, session: SessionDep, transaction: TransactionDep):
        self.session = session
        self.transaction = transaction
