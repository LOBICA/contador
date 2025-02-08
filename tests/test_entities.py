from decimal import Decimal
from uuid import uuid4

from contador import entities


def test_create_book():
    # create new book
    book = entities.Book(name="test book", period="testing")
    assert book

    # recreate existing book
    book_data = {
        "uuid": uuid4(),
        "name": "existing book",
        "period": "existing period",
    }
    book = entities.Book(**book_data)
    assert book
    assert book.uuid == book_data["uuid"]


def test_dump_book(book: entities.Book):
    data = book.model_dump()
    assert data["name"] == book.name
    new_book = entities.Book(**data)
    assert new_book.uuid == book.uuid


def test_create_account(book):
    # create basic account
    assert entities.Account(name="test account")

    # create account in a book
    account = entities.Account(name="test account", book=book)
    assert account.book is book

    # restore existing account
    data = {
        "uuid": uuid4(),
        "name": "test account",
        "initial_balance": 150.00,
        "book": book,
    }
    account = entities.Account(**data)
    assert account.uuid == data["uuid"]
    assert account.balance == data["initial_balance"]


def test_dump_account(account: entities.Account):
    data = account.model_dump()
    assert data["name"] == account.name
    new_account = entities.Account(**data)
    assert new_account.uuid == account.uuid


def test_create_transaction(book, payee):
    # create basic transaction
    assert entities.Transaction(date="2021-01-01", description="test transaction")

    # create transaction in a book
    transaction = entities.Transaction(
        date="2021-01-01", description="test transaction", book=book, payee=payee
    )
    assert transaction.book is book

    # restore existing transaction
    data = {
        "uuid": uuid4(),
        "date": "2021-01-01",
        "description": "test transaction",
        "book": book,
        "payee": payee,
    }
    transaction = entities.Transaction(**data)
    assert transaction.uuid == data["uuid"]


def test_dump_transaction(transaction: entities.Transaction):
    data = transaction.model_dump()
    assert data["description"] == transaction.description
    new_transaction = entities.Transaction(**data)
    assert new_transaction.uuid == transaction.uuid


def test_create_entry(account: entities.Account):
    # create entry in account
    entry = account.add_entry(Decimal(100.00))
    assert entry.amount == Decimal(100.00)
    assert entry.account is account

    # restore existing entry
    data = {
        "uuid": uuid4(),
        "amount": Decimal(100.00),
        "account": account,
    }
    entry = entities.Entry(**data)
    assert entry.uuid == data["uuid"]
    assert entry.amount == data["amount"]


def test_dump_entry(account: entities.Account):
    entry = account.add_entry(Decimal(100.00))
    data = entry.model_dump()
    assert data["amount"] == entry.amount
    new_entry = entities.Entry(**data)
    assert new_entry.uuid == entry.uuid
    assert new_entry.amount == entry.amount
    assert new_entry.account.uuid == account.uuid


def test_validate_transaction_entries(
    account: entities.Account, transaction: entities.Transaction
):
    entry1 = account.add_entry(Decimal(100.00))
    entry2 = account.add_entry(Decimal(-100.00))
    transaction.add_entries([entry1, entry2])

    # validate transaction entries
    transaction.validate_entries()

    # add unbalanced entry
    transaction.entries.clear()
    entry3 = account.add_entry(Decimal(50.00))

    # validate transaction entries
    try:
        transaction.add_entries([entry3])
    except ValueError:
        pass
    else:
        assert False, "Transaction entries are unbalanced"

    # validate transaction entries
    try:
        transaction.validate_entries()
    except ValueError:
        pass
    else:
        assert False, "Transaction entries are unbalanced"


def test_link_documents_and_transactions(
    transaction: entities.Transaction, document: entities.Document
):
    # link transaction and document
    transaction.documents.add(document)
    document.transactions.add(transaction)
    assert transaction.documents.get(document.uuid.hex) is document
    assert document.transactions.get(transaction.uuid.hex) is transaction

    # unlink transaction and document
    del transaction.documents[document.uuid.hex]
    del document.transactions[transaction.uuid.hex]
    assert transaction.documents.get(document.uuid.hex) is None
    assert document.transactions.get(transaction.uuid.hex) is None
