import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

engine = create_engine(TEST_DATABASE_URL)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def client():
    Base.metadata.create_all(bind=engine)
    session = TestSessionLocal()

    def _override_get_db():
        yield session

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    session.close()
    Base.metadata.drop_all(bind=engine)
