import typer

import config
from commands import books_app, quotes_app

cfg = config.Config()

app = typer.Typer(
    name=cfg.APP_NAME,
    help=cfg.APP_SHORT_DESCRIPTION,
)
app.add_typer(
    books_app,
    name="books",
    help="Manage books.",
)
app.add_typer(
    quotes_app,
    name="quotes",
    help="Manage quotes.",
)


if __name__ == "__main__":
    app()
