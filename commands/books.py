import csv
from pathlib import Path
from typing import Optional

import typer
from rich import print
from rich.console import Console
from rich.progress import track
from rich.table import Table
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session
from typing_extensions import Annotated

import config
from models import Author, Book, BookStatus
from repositories import AuthorRepository, BookRepository
from repositories.enums import BookOrder

app = typer.Typer()
cfg = config.Config()
err_console = Console(stderr=True)


@app.command("add")
def add_book(
    book_title: Annotated[
        str,
        typer.Option("--title", "-t", prompt="Book title"),
    ],
    book_author: Annotated[
        str,
        typer.Option("--author", "-a", prompt="Author name"),
    ],
    book_status: Annotated[
        BookStatus,
        typer.Option(
            "--status",
            "-s",
            show_choices=True,
        ),
    ] = BookStatus.pending.value,
    book_fav: Annotated[
        bool,
        typer.Option(
            "--fav",
            "-f",
            is_flag=True,
        ),
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


@app.command("list")
def list_books(
    words_in_title: Annotated[
        list[str],
        typer.Option(
            "--words",
            "-w",
            help="Words in title",
        ),
    ] = None,
    book_author: Annotated[
        str,
        typer.Option("--author", "-a"),
    ] = None,
    book_status: Annotated[
        BookStatus,
        typer.Option("--status", "-s"),
    ] = None,
    book_fav: Annotated[
        bool,
        typer.Option(
            "--fav",
            "-f",
            is_flag=True,
        ),
    ] = None,
    order_by: Annotated[
        BookOrder,
        typer.Option(
            "--order-by",
            show_choices=True,
        ),
    ] = BookOrder.title.value,
    reverse_order: Annotated[
        bool,
        typer.Option(
            "--reverse",
            is_flag=True,
        ),
    ] = False,
):
    book_repo = BookRepository()
    author_repo = AuthorRepository()
    engine = cfg.DB_ENGINE

    with Session(engine) as session:
        try:
            author = None
            if book_author is not None:
                author = author_repo.get_by_name(session, book_author)
                if author is None:
                    err_console.print(
                        "The author specified was not found",
                    )
                    return

            author_id = author.id if author else None
            results = book_repo.list(
                session,
                words=words_in_title,
                author_id=author_id,
                status=book_status,
                fav=book_fav,
                order_by=order_by,
                reverse_order=reverse_order,
            )
            if not len(results):
                err_console.print(
                    "No books with the specified criteria were found in your library",
                )
                return

            table = Table(title="Books", show_lines=True)
            table.add_column("Title", style="bold")
            table.add_column("Author")
            table.add_column("Status")
            table.add_column("Favourite")

            for result in results:
                table.add_row(
                    result["Book"].title.title(),
                    result["Author"].name,
                    result["Book"].status.capitalize(),
                    "Yes" if result["Book"].fav else "No",
                )

            print(table)

        except SQLAlchemyError:
            err_console.print("Oops, something went wrong!")


@app.command("delete")
def delete_book(
    book_title: Annotated[
        str,
        typer.Option(
            "--title",
            "-t",
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


@app.command("export")
def export_books(
    file: Annotated[
        Optional[Path],
        typer.Option(
            "--path",
            help="file path",
        ),
    ] = None,
) -> None:
    book_repo = BookRepository()
    engine = cfg.DB_ENGINE

    with Session(engine) as session:
        try:
            results = book_repo.list(session)
            if not len(results):
                err_console.print(
                    "No books found in your library",
                )
                return

            file_path = file if file is not None else "books.csv"
            with open(file_path, mode="w") as books_file:
                fieldnames = ["id", "title", "author", "status", "fav"]
                writer = csv.DictWriter(books_file, fieldnames=fieldnames)

                writer.writeheader()
                for result in track(results, description="Exporting..."):
                    writer.writerow(
                        {
                            "id": result["Book"].id,
                            "title": result["Book"].title.title(),
                            "author": result["Author"].name,
                            "status": result["Book"].status.capitalize(),
                            "fav": "Yes" if result["Book"].fav else "No",
                        }
                    )

                print("CSV file has been successfully created")

        except SQLAlchemyError:
            err_console.print("Oops, something went wrong! Export couldn't be made")


@app.command("import")
def import_books(
    file: Annotated[
        Optional[Path],
        typer.Option(
            "--path",
            help="file path",
        ),
    ] = None,
) -> None:
    book_repo = BookRepository()
    author_repo = AuthorRepository()
    engine = cfg.DB_ENGINE

    with Session(engine) as session:
        try:
            file_path = file if file is not None else "books.csv"
            with open(file_path) as books_file:
                reader = csv.DictReader(books_file)
                for row in track(reader, description="Importing..."):
                    author_name = row["author"]
                    author = author_repo.get_by_name(session, author_name)
                    if author is None:
                        author = Author(name=author_name)
                        author_repo.add(session, author)

                    book_title = row["title"]
                    book = book_repo.get_by_title(session, book_title)
                    if book is None:
                        book = Book(
                            title=book_title,
                            authors=[author],
                            status=row["status"],
                            fav=True if row["fav"] == "Yes" else False,
                        )
                        book_repo.add(session, book)

                    session.commit()

                print("Import has been successful!")

        except SQLAlchemyError:
            err_console.print("Oops, something went wrong! Import failed")


if __name__ == "__main__":
    app()
