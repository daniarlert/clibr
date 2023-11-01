import typer

import books
import config
import quotes

cfg = config.Config()

app = typer.Typer(
    name=cfg.APP_NAME,
    help=cfg.APP_SHORT_DESCRIPTION,
)
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
