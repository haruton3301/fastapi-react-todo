import os
from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from fastapi.testclient import TestClient

from app.auth import ACCESS_TOKEN_EXPIRES, get_password_hash, create_token
from app.database import Base, get_db
from app.main import app
from app.models.status import Status
from app.models.task import Task
from app.models.user import User

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

engine = create_engine(TEST_DATABASE_URL)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def db():
    """テスト用DBセッションを提供する。テーブル作成/破棄を管理"""
    Base.metadata.create_all(bind=engine)
    session = TestSessionLocal()
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
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpassword"),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture()
def auth_headers(test_user: User) -> dict[str, str]:
    """認証済みヘッダーを提供"""
    token = create_token(test_user.id, "access", ACCESS_TOKEN_EXPIRES)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def test_status(db: Session, test_user: User) -> Status:
    """テスト用ステータスを作成"""
    status = Status(
        name="テストステータス",
        color="#6B7280",
        order=1,
        user_id=test_user.id,
    )
    db.add(status)
    db.commit()
    db.refresh(status)
    return status


@pytest.fixture()
def test_statuses(db: Session, test_user: User) -> list[Status]:
    """テスト用ステータスを3件作成"""
    items = [
        Status(name="未着手", color="#6B7280", order=1, user_id=test_user.id),
        Status(name="進行中", color="#3B82F6", order=2, user_id=test_user.id),
        Status(name="完了", color="#10B981", order=3, user_id=test_user.id),
    ]
    db.add_all(items)
    db.commit()
    for s in items:
        db.refresh(s)
    return items


@pytest.fixture()
def test_task(db: Session, test_user: User, test_status: Status) -> Task:
    """テスト用タスクを作成"""
    task = Task(
        title="テストタスク",
        content="テスト内容",
        due_date=date(2025, 12, 31),
        status_id=test_status.id,
        user_id=test_user.id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@pytest.fixture()
def test_tasks(db: Session, test_user: User, test_status: Status) -> list[Task]:
    """テスト用タスクを3件作成"""
    items = [
        Task(title="タスク1", content="内容1", due_date=date(2025, 6, 1), status_id=test_status.id, user_id=test_user.id),
        Task(title="タスク2", content="内容2", due_date=date(2025, 9, 15), status_id=test_status.id, user_id=test_user.id),
        Task(title="タスク3", content="内容3", due_date=date(2025, 12, 31), status_id=test_status.id, user_id=test_user.id),
    ]
    db.add_all(items)
    db.commit()
    for t in items:
        db.refresh(t)
    return items
