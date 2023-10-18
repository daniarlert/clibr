import typer

import books
import quotes

app = typer.Typer()
app.add_typer(
    books.app,
    name="books",
    help="Manage books.",
)
app.add_typer(
    quotes.app,
    name="quotes",
    help="Manage quotes.",
)


if __name__ == "__main__":
    app()
