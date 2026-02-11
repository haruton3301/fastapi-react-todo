from sqlalchemy import asc, func
from sqlalchemy.orm import Session

from app.models.status import Status
from app.models.task import Task
from app.schemas.status import StatusCreate, StatusUpdate


def get_statuses(db: Session) -> list[Status]:
    """ステータス一覧取得（order昇順）"""
    return db.query(Status).order_by(asc(Status.order)).all()


def get_status(db: Session, status_id: int) -> Status | None:
    """ステータス詳細取得"""
    return db.query(Status).filter(Status.id == status_id).first()


def create_status(db: Session, status_data: StatusCreate) -> Status:
    """ステータス作成（orderは自動採番）"""
    max_order = db.query(func.max(Status.order)).scalar() or 0
    status = Status(**status_data.model_dump(), order=max_order + 1)
    db.add(status)
    db.commit()
    db.refresh(status)
    return status


def update_status(db: Session, status: Status, status_data: StatusUpdate) -> Status:
    """ステータス更新"""
    for key, value in status_data.model_dump().items():
        setattr(status, key, value)

    db.commit()
    db.refresh(status)
    return status


def reorder_statuses(db: Session, status_ids: list[int]) -> list[Status]:
    """ステータス並び替え（IDリスト順にorderを振り直す）"""
    for new_order, status_id in enumerate(status_ids, start=1):
        db.query(Status).filter(Status.id == status_id).update({"order": new_order})
    db.commit()
    return get_statuses(db)


def has_tasks_with_status(db: Session, status_id: int) -> bool:
    """指定ステータスに紐付くタスクが存在するか"""
    return db.query(Task).filter(Task.status_id == status_id).first() is not None


def delete_status(db: Session, status: Status) -> None:
    """ステータス削除"""
    db.delete(status)
    db.commit()
