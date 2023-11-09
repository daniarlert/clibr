import typer
from rich import print
from rich.console import Console
from rich.table import Table
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session
from typing_extensions import Annotated

import config
from models import Quote
from repositories import AuthorRepository, BookRepository, QuoteRepository

app = typer.Typer()
cfg = config.Config()
err_console = Console(stderr=True)


@app.command("add")
def add_quote(
    text: Annotated[
        str,
        typer.Option("--quote", "-q", prompt="Quote"),
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
            )

            if not len(results):
                err_console.print(
                    "No quotes with the specified criteria were found in your library",
                )
                return

            table = Table(title="Quotes", show_lines=True)
            table.add_column("Book", style="bold")
            table.add_column("Quote", overflow=None)
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


if __name__ == "__main__":
    app()
