from datetime import date

from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate


def get_tasks(
    db: Session,
    user_id: int,
    order: str = "desc",
    keyword: str | None = None,
    due_date_from: date | None = None,
    due_date_to: date | None = None,
) -> list[Task]:
    """タスク一覧取得（締切日でソート）"""
    order_func = desc if order == "desc" else asc
    query = db.query(Task).filter(Task.user_id == user_id)
    if keyword:
        query = query.filter(Task.title.contains(keyword) | Task.content.contains(keyword))
    if due_date_from:
        query = query.filter(Task.due_date >= due_date_from)
    if due_date_to:
        query = query.filter(Task.due_date <= due_date_to)
    return query.order_by(order_func(Task.due_date)).all()


def get_task(db: Session, task_id: int, user_id: int) -> Task | None:
    """タスク詳細取得"""
    return db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()


def create_task(db: Session, task_data: TaskCreate, user_id: int) -> Task:
    """タスク作成"""
    task = Task(**task_data.model_dump(), user_id=user_id)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def update_task(db: Session, task: Task, task_data: TaskUpdate) -> Task:
    """タスク更新"""
    for key, value in task_data.model_dump().items():
        setattr(task, key, value)

    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task: Task) -> None:
    """タスク削除"""
    db.delete(task)
    db.commit()
