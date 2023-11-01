import pytest
from sqlmodel import Session, SQLModel, create_engine

from models import Author, Book, Quote
from repositories import AuthorRepository, BookRepository, QuoteRepository


@pytest.fixture
def session():
    test_engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(test_engine)

    with Session(test_engine) as session:
        yield session


def test_book_repository(session: Session):
    book_repo = BookRepository()
    author = Author(name="Tester")
    book = Book(title="Test Book", authors=[author])

    # Test add new book
    book_repo.add(session, book)
    session.commit()

    retrieved_book = book_repo.get_by_title(session, "Test Book")
    assert f"{retrieved_book}" == f"{book}"

    # Test update book
    book.fav = True
    book_repo.update(session, book)
    session.commit()
    session.refresh(book)

    book = book_repo.get_by_title(session, "Test Book")
    assert book.fav is True

    # Test list books
    books = book_repo.list(session)
    assert len(books) != 0

    # Test delete book
    book_repo.delete(session, book.id)
    session.commit()

    book = book_repo.get_by_title(session, "Test Book")
    assert book is None

    session.close()


def test_author_repository(session: Session):
    author_repo = AuthorRepository()
    author = Author(name="Tester")

    # Test add new author
    author_repo.add(session, author)
    session.commit()

    retrieved_author = author_repo.get_by_name(session, "Tester")
    assert f"{retrieved_author}" == f"{author}"

    # Test update author
    author.name = "Brandon Sanderson"
    author_repo.update(session, author)
    session.commit()
    session.refresh(author)

    author = author_repo.get_by_name(session, "Brandon Sanderson")
    assert author.name == "Brandon Sanderson"

    # Test list authors
    authors = author_repo.list(session)
    assert len(authors) != 0

    # Test delete author
    author_repo.delete(session, author.id)
    session.commit()

    author = author_repo.get_by_name(session, "Brandon Sanderson")
    assert author is None

    session.close()


def test_quote_repository(session: Session):
    quote_repo = QuoteRepository()
    author = Author(name="Tester")
    book = Book(title="Test Book", authors=[author])
    quote = Quote(quote="TDD is not important", book=book, book_id=book.id)

    # Test add new quote
    quote_repo.add(session, quote)
    session.commit()

    retrieved_quote = quote_repo.get_by_id(session, 1)
    assert f"{retrieved_quote}" == f"{quote}"

    # Test update quote
    quote.quote = "TDD is important"
    quote_repo.update(session, quote)
    session.commit()
    session.refresh(quote)

    quote = quote_repo.get_by_id(session, 1)
    assert quote.quote == "TDD is important"

    # Test get by quote
    quote = quote_repo.get_by_quote(session, "TDD is important")
    assert quote.quote == "TDD is important"

    # Test list quotes
    quotes = quote_repo.list(session)
    assert len(quotes) != 0

    # Test delete quote
    quote_repo.delete(session, quote.id)
    session.commit()

    quote = quote_repo.get_by_id(session, 1)
    assert quote is None

    session.close()
