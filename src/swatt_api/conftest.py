import pytest
from alembic.config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from alembic import command
from src.swatt_api.config import test_postgresql_url


@pytest.fixture(scope="session")
def test_engine():
    test_engine = create_engine(test_postgresql_url)
    alembic_config = Config("alembic.ini")
    alembic_config.attributes["test_engine"] = test_engine
    command.upgrade(alembic_config, "head")
    yield test_engine
    test_engine.dispose()


@pytest.fixture
def test_session(test_engine):
    with Session(test_engine) as test_session:
        yield test_session
