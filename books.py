import typer
from rich import print
from rich.console import Console
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session
from typing_extensions import Annotated

import config
from models import Author, Book, BookStatus
from repositories import AuthorRepository, BookRepository

app = typer.Typer()
cfg = config.Config()
err_console = Console(stderr=True)


@app.command("add")
def add_book(
    book_title: Annotated[
        str,
        typer.Option("--title", prompt="Book title"),
    ],
    book_author: Annotated[
        str,
        typer.Option("--author", prompt="Author name"),
    ],
    book_status: Annotated[
        BookStatus,
        typer.Option("--status"),
    ] = BookStatus.pending,
    book_fav: Annotated[
        bool,
        typer.Option("--fav"),
    ] = False,
):
    book_repo = BookRepository()
    author_repo = AuthorRepository()
    engine = cfg.DB_ENGINE

    with Session(engine) as session:
        try:
            author = author_repo.get_by_name(session, book_author)
            if author is None:
                author = Author(name=book_author)
                author_repo.add(session, author)
                print(f"{author} is now in the collection")

            book = book_repo.get_by_title(session, book_title)
            if book is None:
                book = Book(
                    title=book_title,
                    authors=[author],
                    status=book_status,
                    fav=book_fav,
                )
                book_repo.add(session, book)
                print(f"adding '{book_title}' by {author.name} to the library")

            session.commit()
        except SQLAlchemyError:
            err_console.print(
                "Oops, something went wrong! Changes have been rolled back"
            )
            session.rollback()


@app.command("delete")
def delete_book(
    book_title: Annotated[
        str,
        typer.Option(
            "--title",
            prompt="Book title",
        ),
    ],
):
    typer.confirm(
        f"Are you sure you want to delete the book '{book_title}'?",
        abort=True,
    )

    book_repo = BookRepository()
    engine = cfg.DB_ENGINE
    with Session(engine) as session:
        try:
            book = book_repo.get_by_title(session, book_title)
            if book is None:
                return

            book_repo.delete(session, book.id)
            session.commit()
        except SQLAlchemyError:
            err_console.print(
                "Oops, something went wrong! Changes have been rolled back"
            )
            session.rollback()


if __name__ == "__main__":
    app()
