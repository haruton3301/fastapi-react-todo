import factory
from factory.alchemy import SQLAlchemyModelFactory
from datetime import date

from app.auth import get_password_hash
from app.models.user import User
from app.models.status import Status
from app.models.task import Task


class UserFactory(SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session = None
        sqlalchemy_session_persistence = "commit"

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda o: f"{o.username}@example.com")
    hashed_password = factory.LazyFunction(lambda: get_password_hash("testpassword"))


class StatusFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Status
        sqlalchemy_session = None
        sqlalchemy_session_persistence = "commit"

    name = factory.Sequence(lambda n: f"ステータス{n}")
    color = "#6B7280"
    order = factory.Sequence(lambda n: n + 1)
    user_id = None


class TaskFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Task
        sqlalchemy_session = None
        sqlalchemy_session_persistence = "commit"

    title = factory.Sequence(lambda n: f"タスク{n}")
    content = "テスト内容"
    due_date = date(2025, 12, 31)
    status_id = None
    user_id = None
