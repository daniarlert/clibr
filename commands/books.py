import csv
from pathlib import Path
from typing import Optional

import typer
from rich import print as pprint
from rich.console import Console
from rich.progress import track
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session
from typing_extensions import Annotated

import config
from models import BookStatus
from repositories import AuthorRepository, BookRepository
from repositories.enums import BookOrder
from .utils import get_or_create_author, get_or_create_book
from .print import print_raw_books_output, print_formatted_books_output

app = typer.Typer()
cfg = config.Config()
err_console = Console(stderr=True)


@app.command(
    "add",
    help="Add a new book to your library",
)
def add_book(
    book_title: Annotated[
        str,
        typer.Option(
            "--title",
            "-t",
            prompt="Title of the book",
            help="Title of the book",
        ),
    ],
    book_author: Annotated[
        str,
        typer.Option(
            "--author",
            "-a",
            prompt="Name of the author",
            help="Name of the author",
        ),
    ],
    book_status: Annotated[
        BookStatus,
        typer.Option(
            "--status",
            "-s",
            show_choices=True,
            help="Status of the book",
        ),
    ] = BookStatus.pending.value,
    book_fav: Annotated[
        bool,
        typer.Option(
            "--fav",
            "-f",
            is_flag=True,
            help="Indicate whether the book is a favorite",
        ),
    ] = False,
):
    engine = cfg.DB_ENGINE

    with Session(engine) as session:
        try:
            author = get_or_create_author(session, book_author)
            get_or_create_book(session, book_title, author, book_status, book_fav)
            session.commit()
        except SQLAlchemyError:
            err_console.print(
                "Oops, something went wrong! Changes have been rolled back"
            )
            session.rollback()


@app.command(
    "update",
    help="Update a book in your library",
)
def update_book(
    book_id: Annotated[
        int,
        typer.Option(
            "--id",
            help="ID of the book to update",
        ),
    ],
    new_title: Annotated[
        str,
        typer.Option(
            "--title",
            "-t",
            help="New title of the book",
        ),
    ] = None,
    new_status: Annotated[
        BookStatus,
        typer.Option(
            "--status",
            "-s",
            help="New book status",
        ),
    ] = None,
    mark_as_fav: Annotated[
        bool,
        typer.Option(
            "--fav",
            "-f",
            is_flag=True,
            help="Indicate whether the book is a favorite",
        ),
    ] = None,
    unmark_as_fav: Annotated[
        bool,
        typer.Option(
            "--unfav",
            is_flag=True,
            help="Unmarks the book as a favorite",
        ),
    ] = None,
):
    book_repo = BookRepository()
    engine = cfg.DB_ENGINE

    with Session(engine) as session:
        try:
            original_book = book_repo.get_by_id(session, book_id)
            if original_book is None:
                pprint(f"No book found with received ID {book_id}")
                return

            if (
                new_title is None
                and new_status is None
                and mark_as_fav is None
                and unmark_as_fav is None
            ):
                pprint(
                    "There are no attributes marked to update. The book hasn't been updated"
                )
                return

            new_fav = mark_as_fav if mark_as_fav else False if unmark_as_fav else None
            book_repo.update(session, book_id, new_title, new_status, new_fav)
            session.commit()
        except SQLAlchemyError as e:
            err_console.print(
                "Oops, something went wrong! The book couldn't be updated"
            )
            if cfg.DEBUG:
                err_console.print(e)

            session.rollback()


@app.command(
    "list",
    help="List books with the option to filter by keywords, author name, status or favorites",
)
def list_books(
    words_in_title: Annotated[
        list[str],
        typer.Option(
            "--words",
            "-w",
            help="List of words to filter books by title",
        ),
    ] = None,
    book_author: Annotated[
        str,
        typer.Option(
            "--author",
            "-a",
            help="Name of the author to filter by",
        ),
    ] = None,
    book_status: Annotated[
        BookStatus,
        typer.Option(
            "--status",
            "-s",
            help="Status of the books to filter by",
        ),
    ] = None,
    book_fav: Annotated[
        bool,
        typer.Option(
            "--fav",
            "-f",
            is_flag=True,
            help="Filter books by whether they are favorites or not",
        ),
    ] = None,
    order_by: Annotated[
        BookOrder,
        typer.Option(
            "--order-by",
            show_choices=True,
            help="Specify the order in which results are displayed",
        ),
    ] = BookOrder.title.value,
    reverse_order: Annotated[
        bool,
        typer.Option(
            "--reverse",
            is_flag=True,
            help="Reverse the order of the results",
        ),
    ] = False,
    limit: Annotated[
        int,
        typer.Option(
            "--limit",
            help="Limit the number of results displayed",
        ),
    ] = None,
    raw: Annotated[
        bool,
        typer.Option(
            "--raw",
            is_flag=True,
            help="Display raw output without formatting",
        ),
    ] = False,
    total: Annotated[
        bool,
        typer.Option(
            "--total",
            is_flag=True,
            help="Display only the total count.",
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
                limit=limit,
            )
            if not len(results):
                err_console.print(
                    "No books with the specified criteria were found in your library",
                )
                return

            if total:
                pprint(f"Total: {len(results)}")
                return

            if raw:
                print_raw_books_output(results)
            else:
                print_formatted_books_output(results)

        except SQLAlchemyError:
            err_console.print("Oops, something went wrong!")


@app.command(
    "delete",
    help="Delete a book form your library",
)
def delete_book(
    book_id: Annotated[
        int,
        typer.Option(
            "--id",
            prompt="ID of the book",
            help="ID of the book",
        ),
    ],
):
    typer.confirm(
        f"Are you sure you want to delete the book with ID '{book_id}'?",
        abort=True,
    )

    engine = cfg.DB_ENGINE
    with Session(engine) as session:
        try:
            BookRepository().delete(session, book_id)
            session.commit()
        except SQLAlchemyError:
            err_console.print(
                "Oops, something went wrong! Changes have been rolled back"
            )
            session.rollback()


@app.command(
    "export",
    help="Export your library into a CSV file",
)
def export_books(
    file: Annotated[
        Optional[Path],
        typer.Option(
            "--path",
            help="Optional path to the file where the books will be exported as a .csv",
        ),
    ] = None,
) -> None:
    book_repo = BookRepository()
    engine = cfg.DB_ENGINE

    with Session(engine) as session:
        try:
            results = book_repo.list(session, order_by=BookOrder.id)
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
                            "title": f"{result["Book"].title.title()}",
                            "author": f"{result["Author"].name}",
                            "status": result["Book"].status.capitalize(),
                            "fav": "Yes" if result["Book"].fav else "No",
                        }
                    )

                pprint("CSV file has been successfully created")

        except SQLAlchemyError:
            err_console.print("Oops, something went wrong! Export couldn't be made")
            session.rollback()


@app.command(
    "import",
    help="Import books into you library from a CSV file",
)
def import_books(
    file: Annotated[
        Optional[Path],
        typer.Option(
            "--path",
            help="Optional path to the file from which books will be imported",
        ),
    ] = None,
) -> None:
    engine = cfg.DB_ENGINE

    with Session(engine) as session:
        try:
            file_path = file if file is not None else "books.csv"
            with open(file_path) as books_file:
                reader = csv.DictReader(books_file)
                for row in track(reader, description="Importing..."):
                    author_name = row["author"]
                    author = get_or_create_author(session, author_name)
                    get_or_create_book(
                        session,
                        row["title"],
                        author,
                        row["status"],
                        True if row["fav"] == "Yes" else False,
                    )

                    session.commit()

                pprint("Import has been successful!")

        except SQLAlchemyError:
            err_console.print("Oops, something went wrong! Import failed")
            session.rollback()


if __name__ == "__main__":
    app()
