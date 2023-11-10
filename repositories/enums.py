from enum import Enum


class BookOrder(str, Enum):
    id = "id"
    title = "title"
    author = "author"


class QuoteOrder(str, Enum):
    id = "id"
    quote = "quote"
    book = "book"
    author = "author"
