from datetime import datetime
from decimal import Decimal
from typing import Dict, Generic, TypeVar
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Entity(BaseModel):
    uuid: UUID = Field(..., default_factory=uuid4)


EntityType = TypeVar("EntityType", bound=Entity)


class Collection(Dict[str, EntityType], Generic[EntityType]):
    def add(self, entity: EntityType):
        self[entity.uuid.hex] = entity


class Payee(Entity):
    name: str


class Entry(Entity):
    amount: Decimal
    account: "Account"
    transaction: "Transaction" | None = None


class Account(Entity):
    name: str
    initial_balance: Decimal = 0
    book: "Book" | None = None
    entries: Collection["Entry"] = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.book:
            self.book.add_account(self)

    @property
    def balance(self) -> Decimal:
        return self.initial_balance + sum(
            [entry.amount for entry in self.entries.values()]
        )

    def add_entry(self, amount: Decimal) -> Entry:
        entry = Entry(amount=amount, account=self)
        self.entries.add(entry)
        return entry


class Transaction(Entity):
    date: datetime
    description: str
    payee: Payee | None = None
    book: "Book" | None = None
    entries: Collection["Entry"] = {}
    documents: Collection["Document"] = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.book:
            self.book.add_transaction(self)

    def validate_entries(self):
        total = sum([entry.amount for entry in self.entries.values()])
        if total != 0:
            raise ValueError("Entries are unbalanced")

    def add_entries(self, entries: list["Entry"]):
        for entry in entries:
            self.entries.add(entry)
            entry.transaction = self
        self.validate_entries()


class Document(Entity):
    date: datetime
    number: str
    type_: str
    book: "Book"
    transactions: Collection[Transaction] = {}


class Book(Entity):
    name: str
    period: str
    accounts: Collection[Account] = {}
    transactions: Collection[Transaction] = {}

    def add_account(self, account: Account):
        self.accounts.add(account)
        account.book = self

    def add_transaction(self, transaction: Transaction):
        self.transactions.add(transaction)
        transaction.book = self
