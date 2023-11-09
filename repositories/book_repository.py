from typing import Optional

from sqlmodel import Session, or_, select

from models import Author, Book, BookAuthorLink, BookStatus

from .base_repository import BaseRepository


class BookRepository(BaseRepository):
    def __init__(self) -> None:
        super().__init__(Book)

    def add(self, session: Session, book: Book) -> None:
        session.add(book)

    def update(self, session: Session, book: Book) -> None:
        stmt = select(self.model_type).where(self.model_type.id == book.id)
        results = session.exec(stmt)
        original_book = results.one()

        original_book.title = book.title
        original_book.status = book.status
        original_book.fav = book.fav

    def get_by_title(self, session: Session, title: str) -> Book | None:
        stmt = select(self.model_type).where(self.model_type.title == title)
        return session.exec(stmt).first()

    # TODO: add order_by
    def list(
        self,
        session: Session,
        words: Optional[list[str]] = None,
        author_id: Optional[int] = None,
        status: Optional[BookStatus] = None,
        fav: Optional[bool] = None,
    ) -> list[Book] | None:
        stmt = select(self.model_type, Author)

        if words is not None:
            title_conditions = [
                self.model_type.title.ilike(f"%{word}%") for word in words
            ]
            stmt = stmt.where(or_(*title_conditions))

        if author_id is not None:
            stmt = stmt.where(Author.id == author_id)

        if status is not None:
            stmt = stmt.where(self.model_type.status == status)

        if fav is not None:
            stmt = stmt.where(self.model_type.fav == fav)

        stmt = stmt.join(BookAuthorLink, self.model_type.id == BookAuthorLink.book_id)
        stmt = stmt.join(Author, Author.id == BookAuthorLink.author_id)

        results = session.exec(stmt)
        books = results.all()
        return books
