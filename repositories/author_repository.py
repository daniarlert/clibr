from sqlmodel import Session, select

from models import Author

from .base_repository import BaseRepository


class AuthorRepository(BaseRepository):
    def __init__(self) -> None:
        super().__init__(Author)

    def add(self, session: Session, author: Author) -> None:
        session.add(author)

    def update(self, session: Session, id: int, new_name: str) -> None:
        stmt = select(self.model_type).where(self.model_type.id == id)
        results = session.exec(stmt)
        original_author = results.one()

        if original_author.name != new_name:
            original_author.name = new_name

    def get_by_name(self, session: Session, name: str) -> Author | None:
        stmt = select(self.model_type).where(self.model_type.name == name)
        return session.exec(stmt).first()

    def list(self, session: Session) -> list[Author]:
        stmt = select(self.model_type)
        results = session.exec(stmt)
        return results.all()
