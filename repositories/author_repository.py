from sqlmodel import Session, select

from models import Author

from .base_repository import BaseRepository


class AuthorRepository(BaseRepository):
    def __init__(self) -> None:
        super().__init__(Author)

    def add(self, session: Session, author: Author) -> None:
        session.add(author)

    def update(self, session: Session, author: Author) -> None:
        stmt = select(self.model_type).where(self.model_type.id == author.id)
        results = session.exec(stmt)
        original_author = results.one()

        original_author.name = author.name

    def get_by_name(self, session: Session, name: str) -> Author | None:
        stmt = select(self.model_type).where(self.model_type.name == name)
        return session.exec(stmt).first()

    def list(self, session: Session) -> list[Author]:
        stmt = select(self.model_type)
        results = session.exec(stmt)
        return results.all()
