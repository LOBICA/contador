from pytest import fixture

from contador import entities


@fixture
def book() -> entities.Book:
    return entities.Book(name="Test Book", period="Testing")
