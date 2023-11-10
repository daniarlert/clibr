from typing import Optional

from sqlmodel import Session, or_, select, desc

from models import Author, Book, BookAuthorLink, Quote

from .base_repository import BaseRepository
from .enums import QuoteOrder


class QuoteRepository(BaseRepository):
    def __init__(self) -> None:
        super().__init__(Quote)

    def get_by_quote(self, session: Session, quote: str) -> Quote | None:
        stmt = select(self.model_type).where(self.model_type.quote == quote)
        return session.exec(stmt).first()

    def add(self, session: Session, quote: Quote) -> None:
        session.add(quote)

    def update(self, session: Session, quote: Quote) -> None:
        stmt = select(self.model_type).where(self.model_type.id == quote.id)
        results = session.exec(stmt)
        original_quote = results.one()

        original_quote.quote = quote.quote

    def list(
        self,
        session: Session,
        words: Optional[list[str]] = None,
        book_id: Optional[int] = None,
        author_id: Optional[int] = None,
        fav: Optional[bool] = None,
        order_by: Optional[QuoteOrder] = QuoteOrder.quote,
        reverse_order: Optional[bool] = False,
    ) -> list[Quote]:
        stmt = select(
            self.model_type,
            Book,
            Author,
        ).where(self.model_type.book_id == Book.id)

        stmt = stmt.join(
            BookAuthorLink, self.model_type.book_id == BookAuthorLink.book_id
        )
        stmt = stmt.join(Author, Author.id == BookAuthorLink.author_id)

        if words is not None:
            quote_conditions = [
                self.model_type.quote.ilike(f"%{word}%") for word in words
            ]
            stmt = stmt.where(or_(*quote_conditions))

        if book_id is not None:
            stmt = stmt.where(self.model_type.id == book_id)

        if author_id is not None:
            stmt = stmt.where(Author.id == author_id)

        if fav is not None:
            stmt = stmt.where(self.model_type.fav == fav)

        order_column = self.model_type.quote
        if order_by == QuoteOrder.author:
            order_column = Author.name
        elif order_by == QuoteOrder.book:
            order_column = Book.title

        stmt = (
            stmt.order_by(desc(order_column))
            if reverse_order
            else stmt.order_by(order_column)
        )

        result = session.exec(stmt)
        return result.all()
