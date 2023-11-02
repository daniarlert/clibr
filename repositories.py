from abc import ABC, abstractclassmethod
from typing import Optional

from sqlmodel import Session, SQLModel, or_, select

from models import Author, Book, BookAuthorLink, BookStatus, Quote


class BaseRepository(ABC):
    def __init__(self, model_type: SQLModel) -> None:
        self.model_type = model_type

    def get_by_id(self, session: Session, id: int) -> SQLModel | None:
        stmt = select(self.model_type).where(self.model_type.id == id)
        return session.exec(stmt).first()

    @abstractclassmethod
    def add(self, session: Session, entity) -> None:
        pass

    @abstractclassmethod
    def update(self, session: Session, entity) -> None:
        pass

    def delete(self, session: Session, id: int) -> None:
        item = self.get_by_id(session, id)
        session.delete(item)

    @abstractclassmethod
    def list(self, session: Session) -> list[SQLModel]:
        pass


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
    ) -> list[Book] | None:
        # stmt = select(self.model_type)
        stmt = select(self.model_type, Author.name.label("author"))

        if words is not None:
            title_conditions = [
                self.model_type.title.ilike(f"%{word}%") for word in words
            ]
            stmt = stmt.where(or_(*title_conditions))

        if author_id is not None:
            stmt = stmt.join(BookAuthorLink).where(
                BookAuthorLink.author_id == author_id
            )

        if status is not None:
            stmt = stmt.where(self.model_type.status == status)

        if fav is not None:
            stmt = stmt.where(self.model_type.fav == fav)

        stmt = stmt.join(BookAuthorLink, self.model_type.id == BookAuthorLink.book_id)
        stmt = stmt.join(Author, Author.id == BookAuthorLink.author_id)

        results = session.exec(stmt)
        books = results.all()
        return books


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

    def search_quote_like(self, session: Session, terms: list[str]) -> list[str]:
        # TODO: implement
        pass

    def list(self, session: Session) -> list[Quote]:
        stmt = select(self.model_type)
        results = session.exec(stmt)
        return results.all()
