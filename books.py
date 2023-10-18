from enum import Enum

import typer

app = typer.Typer()


class BookStatus(str, Enum):
    wanted = "wanted"
    pending = "pending"
    reading = "reading"
    finished = "finished"
    abandoned = "abandoned"


@app.command("add")
def add_book(
    title: str = "",
    author: str = "",
    status: BookStatus = BookStatus.pending,
    fav: bool = False,
):
    print(f"adding book '{title}' by '{author}' with status '{status.value}'")


@app.command("delete")
def delete_book(title: str):
    typer.confirm(
        "Are you sure you want to delete it?",
        abort=True,
    )

    print(f"deleting {title} from library")


if __name__ == "__main__":
    app()
