from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime
from uuid import UUID, uuid4


class Entity(BaseModel):
    uuid: UUID = Field(..., default_factory=uuid4)


class Book(Entity):
    name: str
    period: str
    accounts: list["Account"] = []


class Account(Entity):
    name: str
    balance: float
    book = Book
    transactions: list["Transaction"] = []


class Transaction(Entity):
    date: datetime
    amount: Decimal
    description: str
    from_account: Account | None
    to_account: Account | None


class Document(Entity):
    number: str
    date: datetime
    book: Book
    transactions: list["Transaction"] = []
