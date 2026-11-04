from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db import engine, get_db
from app.main import app


@pytest.fixture
def db_session() -> Iterator[Session]:
    """A session on the migrated test database whose changes are rolled back.

    The test runs inside an outer transaction that's never committed. Commits
    inside the test only release savepoints, so every test starts from the same
    empty tables.
    """
    with engine.connect() as connection:
        transaction = connection.begin()
        with Session(
            bind=connection, join_transaction_mode="create_savepoint"
        ) as session:
            yield session
        transaction.rollback()


@pytest.fixture
def client(db_session: Session) -> Iterator[TestClient]:
    """A client for the real app whose requests use the test's rolled-back session."""
    app.dependency_overrides[get_db] = lambda: db_session
    yield TestClient(app)
    app.dependency_overrides.clear()
