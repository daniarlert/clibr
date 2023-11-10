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
from models import Quote, Author, Book
from repositories import AuthorRepository, BookRepository, QuoteRepository, QuoteOrder

app = typer.Typer()
cfg = config.Config()
err_console = Console(stderr=True)


@app.command("add")
def add_quote(
    text: Annotated[
        str,
        typer.Option(
            "--quote",
            "-q",
            prompt="Quote",
        ),
    ],
    book_title: Annotated[
        str,
        typer.Option("--title", "-t", prompt="Book title"),
    ],
    quote_fav: Annotated[
        bool,
        typer.Option(
            "--fav",
            "-f",
            is_flag=True,
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
                    f"Oops, the book '{book_title}' isn't in the library yet!"
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


@app.command("list")
def list_quotes(
    words_in_quote: Annotated[
        list[str],
        typer.Option(
            "--words",
            "-w",
            help="Words in quote",
        ),
    ] = None,
    book_title: Annotated[
        str,
        typer.Option(
            "--title",
            "-t",
            help="Book title",
        ),
    ] = None,
    book_author: Annotated[
        str,
        typer.Option(
            "--author",
            "-a",
            help="Author name",
        ),
    ] = None,
    quote_fav: Annotated[
        bool,
        typer.Option(
            "--fav",
            "-f",
            is_flag=True,
        ),
    ] = None,
    order_by: Annotated[
        QuoteOrder,
        typer.Option(
            "--order-by",
        ),
    ] = QuoteOrder.quote.value,
    reverse_order: Annotated[
        bool,
        typer.Option(
            "--reverse",
            is_flag=True,
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
            )

            if not len(results):
                err_console.print(
                    "No quotes with the specified criteria were found in your library",
                )
                return

            table = Table(title="Quotes", show_lines=True)
            table.add_column("Book", style="bold")
            table.add_column("Quote", overflow="ignore")
            table.add_column("Author")
            table.add_column("Favourite")

            for result in results:
                table.add_row(
                    result["Book"].title.title(),
                    result["Quote"].quote,
                    result["Author"].name,
                    "Yes" if result["Quote"].fav else "No",
                )

            print(table)

        except SQLAlchemyError:
            err_console.print(
                "Oops, something went wrong!",
            )


@app.command("delete")
def delete_quote(
    quote: Annotated[
        str,
        typer.Option("--quote", "-q", prompt="Quote"),
    ],
):
    typer.confirm(
        "Are you sure you want to delete this quote?",
        abort=True,
    )

    quote_repo = QuoteRepository()
    engine = cfg.DB_ENGINE
    with Session(engine) as session:
        try:
            quote = quote_repo.get_by_quote(session, quote)
            if quote is None:
                return

            quote_repo.delete(session, quote.id)
            session.commit()
        except SQLAlchemyError:
            err_console.print(
                "Oops, something went wrong! Changes have been rolled back"
            )
            session.rollback()


@app.command("export")
def export_quotes(
    file: Annotated[
        Optional[Path],
        typer.Option(
            "--path",
            help="file path",
        ),
    ] = None,
) -> None:
    quote_repo = QuoteRepository()
    engine = cfg.DB_ENGINE

    with Session(engine) as session:
        try:
            results = quote_repo.list(session)
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
                            "quote": result["Quote"].quote,
                            "book": result["Book"].title.title(),
                            "author": result["Author"].name,
                            "fav": "Yes" if result["Quote"].fav else "No",
                        }
                    )

                print("CSV file has been successfully created")

        except SQLAlchemyError:
            err_console.print("Oops, something went wrong! Export couldn't be made")


@app.command("import")
def import_quotes(
    file: Annotated[
        Optional[Path],
        typer.Option(
            "--path",
            help="file path",
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

                print("Import has been successful!")

        except SQLAlchemyError:
            err_console.print("Oops, something went wrong! Import failed")


if __name__ == "__main__":
    app()
