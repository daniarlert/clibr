from rich import print as pprint
from rich.table import Table


def print_raw_books_output(results: list[dict]) -> None:
    print("[bold]id, title, author, status, fav")
    for result in results:
        pprint(
            f"{result['Book'].id}, \"{result['Book'].title}\", {result['Author'].name}, {result['Book'].status}, {'Yes' if result['Book'].fav else 'No'}"
        )


def print_formatted_books_output(results: list[list[dict]]) -> None:
    table = Table(title="Books", show_lines=True)
    table.add_column("ID", style="bold", justify="center")
    table.add_column("Title", style="bold")
    table.add_column("Author")
    table.add_column("Status", justify="center")
    table.add_column("Favourite", justify="center")

    for result in results:
        table.add_row(
            f"{result['Book'].id}",
            result["Book"].title.title(),
            result["Author"].name,
            result["Book"].status.capitalize(),
            "Yes" if result["Book"].fav else "No",
        )

    pprint(table)


def print_raw_quotes_output(results: list[dict]) -> None:
    print("[bold]id, book, quote, author, fav")
    for result in results:
        pprint(
            f"{result['Quote'].id}, \"{result['Book'].title}\", \"{result['Quote'].quote}\", {result['Author'].name}, {'Yes' if result['Quote'].fav else 'No'}"
        )


def print_formatted_quotes_output(results: list[dict]) -> None:
    table = Table(title="Quotes", show_lines=True)
    table.add_column("ID", style="bold", justify="center")
    table.add_column("Book", style="bold")
    table.add_column("Quote", overflow="ignore")
    table.add_column("Author")
    table.add_column("Favourite", justify="center")

    for result in results:
        table.add_row(
            f"{result['Quote'].id}",
            result["Book"].title.title(),
            result["Quote"].quote,
            result["Author"].name,
            "Yes" if result["Quote"].fav else "No",
        )

    pprint(table)
