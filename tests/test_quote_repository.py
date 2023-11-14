from sqlmodel import Session, select

from models import Quote
from repositories import QuoteRepository

from .utils import add_author, add_book, add_quote, session


def test_quote_repository_add(session: Session):
    text_quote = "Remember, the past need not become our future as well."

    author = add_author(session, "Brandon Sanderson")
    book = add_book(session, "Elantris", author)
    quote = add_quote(
        session,
        book,
        text_quote,
    )
    session.commit()

    stmt = select(Quote).where(quote.quote == text_quote)
    result = session.exec(stmt).first()
    assert result is not None
    assert result.quote == result.quote


def test_quote_repository_update(session: Session):
    bad_text_quote = "the past need not become our future as well."
    correct_text_quote = "Remember, the past need not become our future as well."

    quote_repo = QuoteRepository()
    author = add_author(session, "Brandon Sanderson")
    book = add_book(session, "elantris", author)
    quote = add_quote(
        session,
        book,
        bad_text_quote,
    )
    session.commit()

    quote_repo.update(session, quote.id, new_text=correct_text_quote)

    stmt = select(Quote).where(quote.quote == correct_text_quote)
    result = session.exec(stmt).first()
    assert result is not None
    assert result.quote == quote.quote


def test_quote_repository_get_by_quote(session: Session):
    text_quote = "Remember, the past need not become our future as well."

    quote_repo = QuoteRepository()
    author = add_author(session, "Brandon Sanderson")
    book = add_book(session, "Elantris", author)
    quote = Quote(
        quote=text_quote,
        book=book,
        book_id=book.id,
    )
    quote_repo.add(session, quote)
    session.commit()

    retrieved_quote = quote_repo.get_by_quote(session, text_quote)
    assert retrieved_quote is not None
    assert retrieved_quote.id == quote.id
    assert retrieved_quote.quote == quote.quote

    unknown_quote = quote_repo.get_by_quote(session, "Talk is cheap. Show me the code.")
    assert unknown_quote is None


def test_quote_repository_list(session: Session):
    author = add_author(session, "Brandon Sanderson")
    book = add_book(session, "The Final Empire", author)
    quote_repo = QuoteRepository()

    quotes = [
        "You should try not to talk so much, friend. You'll sound far less stupid that way",
        "I've always been very confident in my immaturity.",
        "Men rarely see their own actions as unjustified.",
    ]
    for quote in quotes:
        quote_repo.add(
            session,
            Quote(
                quote=quote,
                book=book,
                book_id=book.id,
            ),
        )

    session.commit()

    results = quote_repo.list(session)
    assert len(results) == len(quotes)


def test_book_repository_list_by_author(session: Session):
    quote_repo = QuoteRepository()
    author_brandon = add_author(session, "Brandon Sanderson")
    author_jordan = add_author(session, "Robert Jordan")
    brandon_book = add_book(session, "The Final Empire", author_brandon)
    jordan_book = add_book(session, "The Eye of the World", author_jordan)

    brandon_quotes = [
        "You should try not to talk so much, friend. You'll sound far less stupid that way",
        "I've always been very confident in my immaturity.",
        "Men rarely see their own actions as unjustified.",
    ]
    for quote in brandon_quotes:
        quote_repo.add(
            session,
            Quote(quote=quote, book=brandon_book, book_id=brandon_book.id),
        )

    jordan_quotes = [
        "Run when you have to, fight when you must, rest when you can.",
    ]
    for quote in jordan_quotes:
        quote_repo.add(
            session,
            Quote(quote=quote, book=jordan_book, book_id=jordan_book.id),
        )

    session.commit()

    brandon_results = quote_repo.list(session, author_id=author_brandon.id)
    assert len(brandon_results) == len(brandon_quotes)

    jordan_results = quote_repo.list(session, author_id=author_jordan.id)
    assert len(jordan_results) == len(jordan_quotes)


def test_quote_repository_list_by_fav(session: Session):
    author = add_author(session, "Brandon Sanderson")
    book = add_book(session, "The Final Empire", author)
    quote_repo = QuoteRepository()

    quotes = [
        "You should try not to talk so much, friend. You'll sound far less stupid that way",
        "I've always been very confident in my immaturity.",
        "Men rarely see their own actions as unjustified.",
    ]
    for quote in quotes:
        quote_repo.add(
            session,
            Quote(
                quote=quote,
                book=book,
                book_id=book.id,
                fav=True if quote == quotes[-1] else False,
            ),
        )

    session.commit()

    results = quote_repo.list(session, fav=False)
    assert len(results) == len(quotes) - 1

    results = quote_repo.list(session, fav=True)
    assert len(results) == 1
