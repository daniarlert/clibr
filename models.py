from enum import Enum
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class BookStatus(str, Enum):
    wanted = "wanted"
    pending = "pending"
    reading = "reading"
    finished = "finished"
    abandoned = "abandoned"


class BookAuthorLink(SQLModel, table=True):
    book_id: Optional[int] = Field(
        default=None,
        foreign_key="book.id",
        primary_key=True,
    )
    author_id: Optional[int] = Field(
        default=None,
        foreign_key="author.id",
        primary_key=True,
    )


class BookQuoteLink(SQLModel, table=True):
    book_id: Optional[int] = Field(
        default=None,
        foreign_key="book.id",
        primary_key=True,
    )
    quote_id: Optional[int] = Field(
        default=None,
        foreign_key="quote.id",
        primary_key=True,
    )


class Book(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True, nullable=False)
    status: BookStatus = BookStatus.pending
    fav: bool = False

    authors: list["Author"] = Relationship(
        back_populates="books",
        link_model=BookAuthorLink,
    )
    quotes: list["Quote"] = Relationship(
        back_populates="books",
        link_model=BookQuoteLink,
    )

    def __str__(self):
        return f'{self.id}: "{self.title}" by {self.author_id}'


class Author(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)

    books: list["Book"] = Relationship(
        back_populates="authors",
        link_model=BookAuthorLink,
    )

    def __str__(self):
        return f"{self.id}: {self.name}"


class Quote(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    quote: str = Field(index=True, nullable=False)

    books: list["Book"] = Relationship(
        back_populates="quotes",
        link_model=BookQuoteLink,
    )

    def __str__(self) -> str:
        return f"'{self.quote}'"
