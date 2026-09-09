import pytest
from alembic.config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import NullPool

from alembic import command
from swatt_api.config import test_postgresql_url


@pytest.fixture(scope="session")
def test_engine():
    test_engine = create_engine(test_postgresql_url, poolclass=NullPool)
    alembic_config = Config("alembic.ini")
    alembic_config.attributes["test_engine"] = test_engine
    command.upgrade(alembic_config, "head")
    yield test_engine
    test_engine.dispose()


@pytest.fixture
def test_session(test_engine):
    test_connection = test_engine.connect()
    test_outer_transaction = test_connection.begin()
    test_session = Session(
        bind=test_connection, join_transaction_mode="create_savepoint"
    )
    yield test_session
    test_session.close()
    test_outer_transaction.rollback()
    test_connection.close()
