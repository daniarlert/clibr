from enum import Enum


class BookOrder(str, Enum):
    title = "title"
    author = "author"


class QuoteOrder(str, Enum):
    quote = "quote"
    book = "book"
    author = "author"
