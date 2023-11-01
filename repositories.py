from abc import ABC, abstractclassmethod

from sqlmodel import Session, SQLModel, select

from models import Author, Book, Quote


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

    def list(self, session: Session) -> None:
        stmt = select(self.model_type)
        results = session.exec(stmt)
        return results.all()


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

    def list_by_book_id(self, session: Session, book_id: int) -> list[Quote]:
        stmt = select(self.model_type).where(self.model_type.book_id == book_id)
        results = session.exec(stmt)
        return results.all()
