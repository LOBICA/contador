from datetime import datetime
from decimal import Decimal
from typing import Annotated, Dict, Generic, Iterable, Optional, TypeVar
from uuid import UUID, uuid4

from pydantic import BaseModel, Field
from pydantic_core import core_schema


class Entity(BaseModel):
    uuid: UUID = Field(..., default_factory=uuid4)


EntityType = TypeVar("EntityType", bound=Entity)


class CollectionType(Dict[str, EntityType], Generic[EntityType]):
    def add(self, entity: EntityType):
        self[entity.uuid.hex] = entity

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        return core_schema.no_info_after_validator_function(cls, handler(dict))


Collection = Annotated[
    CollectionType[EntityType],
    Field(default_factory=CollectionType, exclude=True, repr=False),
]


class Payee(Entity):
    name: str


class Entry(Entity):
    amount: Decimal
    account: "Account"
    transaction: Optional["Transaction"] = None


class Account(Entity):
    name: str
    initial_balance: Decimal = Decimal(0.0)
    book: Optional["Book"] = None
    entries: Collection["Entry"]

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

    def credit(self, amount: Decimal) -> Entry:
        """Take money out of the account"""
        return self.add_entry(-1 * amount)

    def debit(self, amount: Decimal) -> Entry:
        """Put money into the account"""
        return self.add_entry(amount)


class Transaction(Entity):
    date: datetime
    description: str
    book: Optional["Book"] = None
    entries: Collection["Entry"]
    documents: Collection["Document"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.book:
            self.book.add_transaction(self)

    def validate_entries(self):
        total = sum([entry.amount for entry in self.entries.values()])
        if total != 0:
            raise ValueError("Entries are unbalanced")

    def add_entries(self, entries: Iterable[Entry]):
        for entry in entries:
            self.entries.add(entry)
            entry.transaction = self
        self.validate_entries()


class Document(Entity):
    date: datetime
    number: str
    type_: str
    amount: Decimal
    tax_amount: Decimal = Decimal(0.0)
    payee: Optional[Payee] = None
    location: Optional[str] = None
    book: "Book"
    transactions: Collection[Transaction]


class Book(Entity):
    name: str
    period: str
    accounts: Collection[Account]
    transactions: Collection[Transaction]

    def add_account(self, account: Account):
        self.accounts.add(account)
        account.book = self

    def add_transaction(self, transaction: Transaction):
        self.transactions.add(transaction)
        transaction.book = self
