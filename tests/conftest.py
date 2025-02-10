from decimal import Decimal

from pytest import fixture

from contador.core import entities
from contador.core.manager import AccountManager


@fixture
def book() -> entities.Book:
    return entities.Book(name="Test Book", period="Testing")


@fixture
def account(book) -> entities.Account:
    return entities.Account(name="test account", book=book)


@fixture
def payee() -> entities.Payee:
    return entities.Payee(name="Test Payee")


@fixture
def transaction(book, payee) -> entities.Transaction:
    return entities.Transaction(
        date="2021-01-01", description="test transaction", payee=payee, book=book
    )


@fixture
def document(book) -> entities.Document:
    return entities.Document(
        date="2021-01-01",
        number="123",
        type_="invoice",
        amount=Decimal(100.0),
        book=book,
    )


@fixture
def account_manager(book) -> AccountManager:
    return AccountManager(book)
