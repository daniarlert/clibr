import pytest
from sqlmodel import Session, SQLModel, create_engine

from models import Author, Book, BookStatus, Quote
from repositories import BookRepository, QuoteRepository, AuthorRepository


@pytest.fixture
def session():
    test_engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(test_engine)

    with Session(test_engine) as session:
        yield session


def add_book(
    session: Session,
    title: str,
    author: Author,
    status: BookStatus = BookStatus.pending,
    fav: bool = False,
) -> Book:
    book_repo = BookRepository()
    book = Book(
        title=title,
        authors=[author],
        status=status,
        fav=fav,
    )

    book_repo.add(session, book)
    return book


def add_author(
    session: Session,
    name: str,
) -> Author:
    author_repo = AuthorRepository()

    author = Author(name=name)
    author_repo.add(session, author)
    return author


def add_quote(
    session: Session,
    book: Book,
    text: str,
    fav: bool = False,
) -> Quote:
    quote_repo = QuoteRepository()

    quote = Quote(
        quote=text,
        book=book,
        book_id=book.id,
        fav=fav,
    )

    quote_repo.add(session, quote)
    return quote
