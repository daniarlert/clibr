import uuid
from enum import Enum
from uuid import uuid4


class BookStatus(str, Enum):
    wanted = "wanted"
    pending = "pending"
    reading = "reading"
    finished = "finished"
    abandoned = "abandoned"


class Book:
    id: uuid.UUID = uuid4()
    title: str
    author_id: uuid.UUID
    status: BookStatus = BookStatus.pending
    fav: bool = False

    def __str__(self):
        return f'{self.id}: "{self.title}" by {self.author_id}'


class Quote:
    id: uuid.UUID = uuid4()
    quote: str
    book_id: uuid.UUID
    author_id: uuid.UUID

    def __str__(self):
        return f'{self.id}: "{self.quote}" by {self.author_id} at "{self.book_id}"'


class Author:
    id: uuid.UUID = uuid4()
    name: str

    def __str__(self):
        return f"{self.id}: {self.name}"
