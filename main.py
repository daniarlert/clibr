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
    help="Manage and explore your book collection",
)
app.add_typer(
    quotes_app,
    name="quotes",
    help="Manage and explore your quotes",
)


@app.callback()
def main(
    debug: bool = typer.Option(
        False,
        "--debug",
        is_flag=True,
        help="Enable debugging information",
    ),
):
    if debug:
        cfg.DEBUG = True


if __name__ == "__main__":
    app()
