from sqlmodel import Session

from .utils import session
from models import Author, Book, Quote
from repositories import AuthorRepository, QuoteRepository


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
