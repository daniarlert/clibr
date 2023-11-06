from sqlmodel import Session, select

from .utils import session
from models import Book, BookStatus
from repositories import BookRepository

from .utils import add_book


def test_book_repository_add(session: Session):
    book = add_book(session, "Elantris", "Brandon Sanderson")
    session.commit()

    stmt = select(Book).where(Book.title == "Elantris")
    result = session.exec(stmt).first()
    assert result is not None
    assert result.title == book.title


def test_book_repository_update(session: Session):
    book_repo = BookRepository()
    book = add_book(session, "elantris", "Brandon Sanderson")
    session.commit()

    book.title = "Elantris"
    book_repo.update(session, book)

    stmt = select(Book).where(Book.title == "Elantris")
    result = session.exec(stmt).first()
    assert result is not None
    assert result.title == book.title


def test_book_repository_get_by_title(session: Session):
    book_repo = BookRepository()
    book = add_book(session, "Elantris", "Brandon Sanderson")
    session.commit()

    retrieved_book = book_repo.get_by_title(session, "Elantris")
    assert retrieved_book is not None
    assert retrieved_book.id == book.id
    assert retrieved_book.title == book.title

    unknown_book = book_repo.get_by_title(session, "The Final Empire")
    assert unknown_book is None


def test_book_repository_list(session: Session):
    book_repo = BookRepository()

    titles = ["The Sunlit Man", "Elantris", "The Final Empire"]
    for title in titles:
        add_book(session, title, "Brandon Sanderson")

    session.commit()

    results = book_repo.list(session)
    assert len(results) == len(titles)


def test_book_repository_list_by_author(session: Session):
    pass


def test_book_repository_list_by_status(session: Session):
    book_repo = BookRepository()

    titles = ["The Sunlit Man", "Elantris", "The Final Empire"]
    for idx, title in enumerate(titles):
        if idx == len(titles) - 1:
            add_book(session, title, "Brandon Sanderson", status=BookStatus.finished)
        else:
            add_book(session, title, "Brandon Sanderson")

    session.commit()

    results = book_repo.list(session, status=BookStatus.pending)
    assert len(results) == 2

    results = book_repo.list(session, status=BookStatus.finished)
    assert len(results) == 1


def test_book_repository_list_by_fav(session: Session):
    book_repo = BookRepository()

    titles = ["The Sunlit Man", "Elantris", "The Final Empire"]
    for idx, title in enumerate(titles):
        if idx == len(titles) - 1:
            add_book(session, title, "Brandon Sanderson", fav=True)
        else:
            add_book(session, title, "Brandon Sanderson")

    session.commit()

    results = book_repo.list(session, fav=False)
    assert len(results) == 2

    results = book_repo.list(session, fav=True)
    assert len(results) == 1
