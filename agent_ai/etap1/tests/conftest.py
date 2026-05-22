import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ustawiamy środowisko testowe ZANIM zaimportujemy app.main i app.database
os.environ["ENVIRONMENT"] = "test"

from app.core.settings import Settings
from app.database import Base, get_db
from app.main import app


test_settings = Settings(_env_file=".env.test")

TEST_ENGINE = create_engine(
    test_settings.database_url,
    connect_args={"check_same_thread": False}
    if test_settings.database_url.startswith("sqlite")
    else {},
)

TestSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=TEST_ENGINE,
)


def override_get_db():
    db = TestSessionLocal()

    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def client():
    Base.metadata.create_all(bind=TEST_ENGINE)

    with TestClient(app) as c:
        yield c

    Base.metadata.drop_all(bind=TEST_ENGINE)