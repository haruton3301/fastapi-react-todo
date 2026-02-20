from datetime import date

from sqlalchemy.orm import Session

from app.models.status import Status
from app.models.task import Task


def create_status_in_db(
    db: Session,
    *,
    user_id: int,
    name: str = "テストステータス",
    color: str = "#6B7280",
    order: int = 1,
) -> Status:
    status = Status(name=name, color=color, order=order, user_id=user_id)
    db.add(status)
    db.commit()
    db.refresh(status)
    return status


def create_task_in_db(
    db: Session,
    *,
    user_id: int,
    title: str = "テストタスク",
    content: str = "テスト内容",
    due_date: date = date(2025, 12, 31),
    status_id: int | None = None,
) -> Task:
    if status_id is None:
        status = create_status_in_db(db, user_id=user_id)
        status_id = status.id
    task = Task(title=title, content=content, due_date=due_date, status_id=status_id, user_id=user_id)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task
