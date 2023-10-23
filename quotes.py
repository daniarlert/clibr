import typer
from typing_extensions import Annotated

from models import Author, Book, Quote

app = typer.Typer()


@app.command("add")
def add_quote(
    text: Annotated[
        str,
        typer.Option("--quote", prompt="Quote"),
    ],
    book_title: Annotated[
        str,
        typer.Option("--book", prompt="Book title"),
    ],
    book_author: Annotated[
        str,
        typer.Option("--author", prompt="Author's name"),
    ],
):
    author = Author()
    author.name = book_author

    book = Book()
    book.title = book_title
    book.author_id = author.id

    quote = Quote()
    quote.quote = text
    quote.author_id = author.id
    quote.book_id = book.id

    print(author)
    print(book)
    print(quote)


@app.command("delete")
def delete_quote(
    quote: Annotated[
        str,
        typer.Option(prompt="Quote"),
    ],
):
    typer.confirm(
        "Are you sure you want to delete it?",
        abort=True,
    )

    print(f"deleting '{quote}'")


if __name__ == "__main__":
    app()
