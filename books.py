import typer
from typing_extensions import Annotated

from models import Author, Book, BookStatus

app = typer.Typer()


@app.command("add")
def add_book(
    title: Annotated[
        str,
        typer.Option(prompt="Book title"),
    ],
    book_author: Annotated[
        str,
        typer.Option("--author", prompt="Author name"),
    ],
    status: BookStatus = BookStatus.pending,
    fav: bool = False,
):
    author = Author()
    author.name = book_author

    book = Book()
    book.author_id = author.id
    book.title = title
    book.status = status
    book.fav = fav

    print(book)
    print(book_author)


@app.command("delete")
def delete_book(
    title: Annotated[
        str,
        typer.Option(
            prompt="Book title",
        ),
    ],
):
    typer.confirm(
        "Are you sure you want to delete it?",
        abort=True,
    )

    print(f"deleting {title} from library")


if __name__ == "__main__":
    app()
