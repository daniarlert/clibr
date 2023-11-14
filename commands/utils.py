from sqlmodel import Session
from rich import print as pprint

from models import Author, Book, BookStatus
from repositories import AuthorRepository, BookRepository


def get_or_create_author(session: Session, author_name: str) -> Author:
    author_repo = AuthorRepository()
    author = author_repo.get_by_name(session, author_name)
    if author is None:
        author = Author(name=author_name)
        author_repo.add(session, author)
        pprint(f"{author} is now in the collection")

    return author


def get_or_create_book(
    session: Session,
    book_title: str,
    author: Author,
    book_status: BookStatus,
    book_fav: bool,
) -> Book:
    book_repo = BookRepository()
    book = book_repo.get_by_title(session, book_title)

    if book is None:
        book = Book(
            title=book_title,
            authors=[author],
            status=book_status,
            fav=book_fav,
        )
        book_repo.add(session, book)
        pprint(f'Added "{book_title}" by {author.name} to the library')
    else:
        pprint(f'Book "{book_title}" is already in the library')

    return book
