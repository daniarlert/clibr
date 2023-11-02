import typer
from rich import print
from rich.console import Console
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session
from typing_extensions import Annotated

import config
from models import Quote
from repositories import BookRepository, QuoteRepository

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
        typer.Option("--fav", "-f"),
    ] = False,
):
    book_repo = BookRepository()
    quote_repo = QuoteRepository()
    engine = cfg.DB_ENGINE

    with Session(engine) as session:
        try:
            book = book_repo.get_by_title(session, book_title)
            if book is None:
                err_console(f"Oops, the book '{book_title}' isn't in the library yet!")
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
