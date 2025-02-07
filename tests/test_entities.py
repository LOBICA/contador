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
    assert new_book
