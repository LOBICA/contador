from pytest import fixture

from contador import entities


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
        date="2021-01-01", number="123", type_="invoice", book=book
    )
