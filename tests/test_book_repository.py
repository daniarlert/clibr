from audioop import add
from sqlmodel import Session, select

from models import Book, BookStatus
from repositories import BookRepository

from .utils import add_author, add_book, session


def test_book_repository_add(session: Session):
    author = add_author(session, "Brandon Sanderson")
    book = add_book(session, "Elantris", author)
    session.commit()

    stmt = select(Book).where(Book.title == "Elantris")
    result = session.exec(stmt).first()
    assert result is not None
    assert result.title == book.title


def test_book_repository_update(session: Session):
    book_repo = BookRepository()
    author = add_author(session, "Brandon Sanderson")
    book = add_book(session, "elantris", author)
    session.commit()

    book.title = "Elantris"
    book_repo.update(session, book)

    stmt = select(Book).where(Book.title == "Elantris")
    result = session.exec(stmt).first()
    assert result is not None
    assert result.title == book.title


def test_book_repository_get_by_title(session: Session):
    book_repo = BookRepository()
    author = add_author(session, "Brandon Sanderson")
    book = add_book(session, "Elantris", author)
    session.commit()

    retrieved_book = book_repo.get_by_title(session, "Elantris")
    assert retrieved_book is not None
    assert retrieved_book.id == book.id
    assert retrieved_book.title == book.title

    unknown_book = book_repo.get_by_title(session, "The Final Empire")
    assert unknown_book is None


def test_book_repository_list(session: Session):
    book_repo = BookRepository()
    author = add_author(session, "Brandon Sanderson")
    titles = ["The Sunlit Man", "Elantris", "The Final Empire"]
    for title in titles:
        add_book(session, title, author)

    session.commit()

    results = book_repo.list(session)
    assert len(results) == len(titles)


def test_book_repository_list_by_author(session: Session):
    book_repo = BookRepository()
    author_brandon = add_author(session, "Brandon Sanderson")
    author_jordan = add_author(session, "Robert Jordan")
    titles = [
        ("The Sunlit Man", author_brandon),
        ("Elantris", author_brandon),
        ("The Eye of the World", author_jordan),
    ]
    for title, author in titles:
        add_book(session, title, author)

    session.commit()
    results = book_repo.list(session)
    assert len(results) == len(titles)

    brandon_results = book_repo.list(session, author_id=author_brandon.id)
    assert len(brandon_results) == len(titles) - 1

    jordan_results = book_repo.list(session, author_id=author_jordan.id)
    assert len(jordan_results) == 1


def test_book_repository_list_by_status(session: Session):
    book_repo = BookRepository()
    author = add_author(session, "Brandon Sanderson")

    titles = ["The Sunlit Man", "Elantris", "The Final Empire"]
    for title in titles:
        add_book(
            session,
            title,
            author,
            status=BookStatus.finished if title == titles[-1] else BookStatus.pending,
        )

    session.commit()

    results = book_repo.list(session, status=BookStatus.pending)
    assert len(results) == len(titles) - 1

    results = book_repo.list(session, status=BookStatus.finished)
    assert len(results) == 1


def test_book_repository_list_by_fav(session: Session):
    book_repo = BookRepository()
    author = add_author(session, "Brandon Sanderson")
    titles = ["The Sunlit Man", "Elantris", "The Final Empire"]
    for title in titles:
        add_book(
            session,
            title,
            author,
            fav=True if title == titles[-1] else False,
        )

    session.commit()

    results = book_repo.list(session, fav=False)
    assert len(results) == len(titles) - 1

    results = book_repo.list(session, fav=True)
    assert len(results) == 1
