import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from fastapi.testclient import TestClient

from app.auth import ACCESS_TOKEN_EXPIRES, create_token
from app.database import Base, get_db
from app.main import app
from app.models.status import Status
from app.models.task import Task
from app.models.user import User
from tests.factories import UserFactory, StatusFactory, TaskFactory

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

engine = create_engine(TEST_DATABASE_URL)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def db():
    """テスト用DBセッションを提供する。テーブル作成/破棄を管理"""
    Base.metadata.create_all(bind=engine)
    session = TestSessionLocal()
    UserFactory._meta.sqlalchemy_session = session
    StatusFactory._meta.sqlalchemy_session = session
    TaskFactory._meta.sqlalchemy_session = session
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db: Session):
    """テスト用HTTPクライアントを提供する。DI overrideでテスト用セッションを注入"""
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def test_user(db: Session) -> User:
    """テスト用ユーザーを作成"""
    return UserFactory(username="testuser", email="test@example.com")


@pytest.fixture()
def auth_headers(test_user: User) -> dict[str, str]:
    """認証済みヘッダーを提供"""
    token = create_token(test_user.id, "access", ACCESS_TOKEN_EXPIRES)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def test_status(db: Session, test_user: User) -> Status:
    """テスト用ステータスを作成"""
    return StatusFactory(name="テストステータス", color="#6B7280", order=1, user_id=test_user.id)


@pytest.fixture()
def test_statuses(db: Session, test_user: User) -> list[Status]:
    """テスト用ステータスを3件作成"""
    return [
        StatusFactory(name="未着手", color="#6B7280", order=1, user_id=test_user.id),
        StatusFactory(name="進行中", color="#3B82F6", order=2, user_id=test_user.id),
        StatusFactory(name="完了", color="#10B981", order=3, user_id=test_user.id),
    ]


@pytest.fixture()
def test_task(db: Session, test_user: User, test_status: Status) -> Task:
    """テスト用タスクを作成"""
    return TaskFactory(title="テストタスク", user_id=test_user.id, status_id=test_status.id)


@pytest.fixture()
def test_tasks(db: Session, test_user: User, test_status: Status) -> list[Task]:
    """テスト用タスクを3件作成"""
    from datetime import date
    return [
        TaskFactory(title="タスク1", content="内容1", due_date=date(2025, 6, 1), user_id=test_user.id, status_id=test_status.id),
        TaskFactory(title="タスク2", content="内容2", due_date=date(2025, 9, 15), user_id=test_user.id, status_id=test_status.id),
        TaskFactory(title="タスク3", content="内容3", due_date=date(2025, 12, 31), user_id=test_user.id, status_id=test_status.id),
    ]
