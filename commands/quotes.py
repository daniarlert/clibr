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
from models import Quote, Author, Book
from repositories import (
    AuthorRepository,
    BookRepository,
    QuoteRepository,
    QuoteOrder,
)
from .print import print_raw_quotes_output, print_formatted_quotes_output

app = typer.Typer()
cfg = config.Config()
err_console = Console(stderr=True)


@app.command(
    "add",
    help="Add a new quote",
)
def add_quote(
    text: Annotated[
        str,
        typer.Option(
            "--quote",
            "-q",
            prompt="Quote",
            help="Quote",
        ),
    ],
    book_title: Annotated[
        str,
        typer.Option(
            "--title",
            "-t",
            prompt="Title of the book",
            help="Title of the book",
        ),
    ],
    quote_fav: Annotated[
        bool,
        typer.Option(
            "--fav",
            "-f",
            is_flag=True,
            help="Indicate whether the quote is a favorite",
        ),
    ] = False,
):
    book_repo = BookRepository()
    quote_repo = QuoteRepository()
    engine = cfg.DB_ENGINE

    with Session(engine) as session:
        try:
            book = book_repo.get_by_title(session, book_title)
            if book is None:
                err_console.print(
                    f'Oops, the book "{book_title}" isn\'t in the library yet!'
                )
                return

            quote = Quote(
                quote=text,
                book=book,
                book_id=book.id,
                fav=quote_fav,
            )
            quote_repo.add(session, quote)
            print("Quote added successfully!")

            session.commit()
        except SQLAlchemyError:
            err_console.print(
                "Oops, something went wrong! Changes have been rolled back"
            )
            session.rollback()


@app.command(
    "update",
    help="Update a quote",
)
def update(
    quote_id: Annotated[
        int,
        typer.Option(
            "--id",
            help="ID of the quote to update",
        ),
    ],
    new_text: Annotated[
        str,
        typer.Option(
            "--quote",
            "-q",
            help="New text for the quote",
        ),
    ] = None,
    new_book_title: Annotated[
        str,
        typer.Option(
            "--title",
            "-t",
            help="Title of the book",
        ),
    ] = None,
    mark_as_fav: Annotated[
        bool,
        typer.Option(
            "--fav",
            "-f",
            is_flag=True,
            help="Indicate whether the quote is a favorite",
        ),
    ] = None,
    unmark_as_fav: Annotated[
        bool,
        typer.Option(
            "--unfav",
            is_flag=True,
            help="Unmarks the quote as a favorite",
        ),
    ] = None,
):
    book_repo = BookRepository()
    quote_repo = QuoteRepository()
    engine = cfg.DB_ENGINE

    with Session(engine) as session:
        try:
            original_quote = quote_repo.get_by_id(session, quote_id)
            if original_quote is None:
                pprint(f"No quote found with received ID {quote_id}")
                return
            if (
                new_text is None
                and new_book_title is None
                and mark_as_fav is None
                and unmark_as_fav is None
            ):
                pprint(
                    "There are no attributes marked to update. The quote hasn't been updated"
                )
                return

            new_book = None
            if new_book_title:
                book_repo.get_by_title(session, new_book_title)
                if new_book is None:
                    err_console.print(
                        f'The book "{new_book_title}" was not found',
                    )
                    return

            new_fav = mark_as_fav if mark_as_fav else False if unmark_as_fav else None
            quote_repo.update(session, quote_id, new_text, new_book, new_fav)

            session.commit()

        except SQLAlchemyError as e:
            err_console.print(
                "Oops, something went wrong! The quote couldn't be updated"
            )
            if cfg.DEBUG:
                err_console.print(e)

            session.rollback()


@app.command(
    "list",
    help="List quotes with the option to filter by keywords, author, book or favorites",
)
def list_quotes(
    words_in_quote: Annotated[
        list[str],
        typer.Option(
            "--words",
            "-w",
            help="List of words to filter quotes by content",
        ),
    ] = None,
    book_title: Annotated[
        str,
        typer.Option(
            "--title",
            "-t",
            help="Title of the book to filter by",
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
    quote_fav: Annotated[
        bool,
        typer.Option(
            "--fav",
            "-f",
            is_flag=True,
            help="Filter books by whether they are favorites or not",
        ),
    ] = None,
    order_by: Annotated[
        QuoteOrder,
        typer.Option(
            "--order-by",
            help="Specify the order in which results are displayed",
        ),
    ] = QuoteOrder.quote.value,
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
    quote_repo = QuoteRepository()
    author_repo = AuthorRepository()
    book_repo = BookRepository()
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

            book = None
            if book_title is not None:
                book = book_repo.get_by_title(session, book_title)
                if book is None:
                    err_console.print(
                        "The book specified was not found",
                    )
                    return

            book_id = book.id if book else None

            results = quote_repo.list(
                session,
                words=words_in_quote,
                book_id=book_id,
                author_id=author_id,
                fav=quote_fav,
                order_by=order_by,
                reverse_order=reverse_order,
                limit=limit,
            )

            if not len(results):
                err_console.print(
                    "No quotes with the specified criteria were found in your library",
                )
                return
            
            if total:
                pprint(f"Total: {len(results)}")
                return

            if raw:
                print_raw_quotes_output(results)
            else:
                print_formatted_quotes_output(results)

        except SQLAlchemyError:
            err_console.print(
                "Oops, something went wrong!",
            )


@app.command(
    "delete",
    help="Delete a quote",
)
def delete_quote(
    quote_id: Annotated[
        int,
        typer.Option(
            "--id",
            prompt="Quote ID",
            help="ID of the quote to delete",
        ),
    ],
):
    typer.confirm(
        "Are you sure you want to delete the quote with id '{quote_id}'?",
        abort=True,
    )

    engine = cfg.DB_ENGINE
    with Session(engine) as session:
        try:
            QuoteRepository().delete(session, quote_id)
            session.commit()
        except SQLAlchemyError:
            err_console.print(
                "Oops, something went wrong! Changes have been rolled back"
            )
            session.rollback()


@app.command(
    "export",
    help="Export your quotes into a CSV file",
)
def export_quotes(
    file: Annotated[
        Optional[Path],
        typer.Option(
            "--path",
            help="Optional path to the file where the quotes will be exported as a .csv",
        ),
    ] = None,
) -> None:
    quote_repo = QuoteRepository()
    engine = cfg.DB_ENGINE

    with Session(engine) as session:
        try:
            results = quote_repo.list(session, order_by=QuoteOrder.id)
            if not len(results):
                err_console.print(
                    "No quotes found in your library",
                )
                return

            file_path = file if file is not None else "quotes.csv"
            with open(file_path, mode="w") as quotes_file:
                fieldnames = ["id", "quote", "book", "author", "fav"]
                writer = csv.DictWriter(quotes_file, fieldnames=fieldnames)

                writer.writeheader()
                for result in track(results, description="Exporting..."):
                    writer.writerow(
                        {
                            "id": result["Quote"].id,
                            "quote": f"{result["Quote"].quote}",
                            "book": f"{result["Book"].title.title()}",
                            "author": f"{result["Author"].name}",
                            "fav": "Yes" if result["Quote"].fav else "No",
                        }
                    )

                pprint("CSV file has been successfully created")

        except SQLAlchemyError:
            err_console.print("Oops, something went wrong! Export couldn't be made")


@app.command(
    "import",
    help="Import your quotes from a CSV file",
)
def import_quotes(
    file: Annotated[
        Optional[Path],
        typer.Option(
            "--path",
            help="Optional path to the file from which quotes will be imported",
        ),
    ] = None,
) -> None:
    author_repo = AuthorRepository()
    book_repo = BookRepository()
    quote_repo = QuoteRepository()
    engine = cfg.DB_ENGINE

    with Session(engine) as session:
        try:
            file_path = file if file is not None else "quotes.csv"
            with open(file_path) as books_file:
                reader = csv.DictReader(books_file)
                for row in track(reader, description="Importing..."):
                    author_name = row["author"]
                    author = author_repo.get_by_name(session, author_name)
                    if author is None:
                        author = Author(name=author_name)
                        author_repo.add(session, author)

                    book_title = row["book"]
                    book = book_repo.get_by_title(session, book_title)
                    if book is None:
                        book = Book(
                            title=book_title,
                            authors=[author],
                        )
                        book_repo.add(session, book)

                    quote_text = row["quote"]
                    quote = quote_repo.get_by_quote(session, quote_text)
                    if quote is None:
                        quote = Quote(
                            quote=quote_text,
                            book=book,
                            book_id=book.id,
                            fav=True if row["fav"] == "Yes" else False,
                        )
                        quote_repo.add(session, quote)

                    session.commit()

                pprint("Import has been successful!")

        except SQLAlchemyError:
            err_console.print("Oops, something went wrong! Import failed")


if __name__ == "__main__":
    app()
