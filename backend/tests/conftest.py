from collections.abc import Iterator

import pytest
from sqlalchemy.orm import Session

from app.db import engine


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
