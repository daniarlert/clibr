import pytest
from sqlmodel import Session, SQLModel, create_engine

from models import Author, Book, BookStatus
from repositories import BookRepository


@pytest.fixture
def session():
    test_engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(test_engine)

    with Session(test_engine) as session:
        yield session


def add_book(
    session: Session,
    title: str,
    author_name: str,
    status: BookStatus = BookStatus.pending,
    fav: bool = False,
) -> Book:
    book_repo = BookRepository()
    author = Author(name=author_name)
    book = Book(
        title=title,
        authors=[author],
        status=status,
        fav=fav,
    )

    book_repo.add(session, book)
    return book
