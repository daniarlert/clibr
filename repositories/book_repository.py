from typing import Optional

from sqlmodel import Session, or_, select, desc

from models import Author, Book, BookAuthorLink, BookStatus

from .base_repository import BaseRepository
from .enums import BookOrder


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

    def list(
        self,
        session: Session,
        words: Optional[list[str]] = None,
        author_id: Optional[int] = None,
        status: Optional[BookStatus] = None,
        fav: Optional[bool] = None,
        order_by: Optional[BookOrder] = BookOrder.title,
        reverse_order: bool = False,
        limit: Optional[int] = None,
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

        order_column = self.model_type.title
        if order_by == BookOrder.author:
            order_column = Author.name
        elif order_by == BookOrder.id:
            order_column == self.model_type.id

        stmt = (
            stmt.order_by(desc(order_column))
            if reverse_order
            else stmt.order_by(order_column)
        )

        if limit is not None:
            stmt = stmt.limit(limit)

        results = session.exec(stmt)
        books = results.all()
        return books
