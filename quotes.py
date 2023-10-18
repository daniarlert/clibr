import typer

app = typer.Typer()


@app.command("add")
def add_quote(quote: str = "", book: str = "", author: str = ""):
    print(f"adding quote '{quote}' from '{author}' at book '{book}'")


@app.command("delete")
def delete_quote(quote: str):
    typer.confirm(
        "Are you sure you want to delete it?",
        abort=True,
    )

    print(f"deleting '{quote}'")


if __name__ == "__main__":
    app()
