from sqlalchemy import asc, func, select
from sqlalchemy.orm import Session

from app.models.status import Status
from app.models.task import Task
from app.schemas.status import StatusCreate, StatusUpdate


def get_statuses(db: Session, user_id: int) -> list[Status]:
    return (
        db.scalars(
            select(Status)
            .where(Status.user_id == user_id)
            .order_by(asc(Status.order))
        )
        .all()
    )


def get_status(db: Session, status_id: int, user_id: int) -> Status | None:
    return db.scalars(
        select(Status).where(Status.id == status_id, Status.user_id == user_id)
    ).first()


def create_status(db: Session, status_data: StatusCreate, user_id: int) -> Status:
    max_order = (
        db.scalar(
            select(func.max(Status.order)).where(Status.user_id == user_id)
        )
        or 0
    )
    status = Status(**status_data.model_dump(), order=max_order + 1, user_id=user_id)
    db.add(status)
    db.commit()
    db.refresh(status)
    return status


def update_status(db: Session, status: Status, status_data: StatusUpdate) -> Status:
    for key, value in status_data.model_dump().items():
        setattr(status, key, value)
    db.commit()
    db.refresh(status)
    return status


def reorder_statuses(db: Session, status_ids: list[int], user_id: int) -> list[Status]:
    for new_order, status_id in enumerate(status_ids, start=1):
        status = db.scalars(
            select(Status).where(Status.id == status_id, Status.user_id == user_id)
        ).first()
        if status:
            status.order = new_order
    db.commit()
    return get_statuses(db, user_id)


def has_tasks_with_status(db: Session, status_id: int) -> bool:
    return (
        db.scalars(select(Task).where(Task.status_id == status_id)).first()
        is not None
    )


def delete_status(db: Session, status: Status) -> None:
    db.delete(status)
    db.commit()
