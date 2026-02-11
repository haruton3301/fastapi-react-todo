from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.crud import status as status_crud
from app.models.status import Status
from app.schemas.status import (
    StatusCreate, StatusUpdate, StatusReorder,
    StatusResponse, StatusListResponse,
)

router = APIRouter(prefix="/statuses", tags=["statuses"])


def get_status_or_404(
    status_id: int,
    db: Session = Depends(get_db),
) -> Status:
    """ステータス取得（存在しない場合は404）"""
    status = status_crud.get_status(db, status_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Status not found")
    return status


@router.get("", response_model=StatusListResponse)
def list_statuses(
    db: Session = Depends(get_db),
):
    """ステータス一覧取得（order順）"""
    statuses = status_crud.get_statuses(db)
    return StatusListResponse(statuses=statuses)


@router.get("/{status_id}", response_model=StatusResponse)
def get_status(
    status: Status = Depends(get_status_or_404),
):
    """ステータス詳細取得"""
    return status


@router.post("", response_model=StatusResponse, status_code=201)
def create_status(
    status_data: StatusCreate,
    db: Session = Depends(get_db),
):
    """ステータス作成"""
    return status_crud.create_status(db, status_data)


@router.put("/reorder", response_model=StatusListResponse)
def reorder_statuses(
    reorder_data: StatusReorder,
    db: Session = Depends(get_db),
):
    """ステータス並び替え"""
    all_ids = {s.id for s in status_crud.get_statuses(db)}
    request_ids = set(reorder_data.order)
    if request_ids != all_ids:
        raise HTTPException(
            status_code=400,
            detail="全てのステータスIDを過不足なく指定してください",
        )
    statuses = status_crud.reorder_statuses(db, reorder_data.order)
    return StatusListResponse(statuses=statuses)


@router.put("/{status_id}", response_model=StatusResponse)
def update_status(
    status_data: StatusUpdate,
    status: Status = Depends(get_status_or_404),
    db: Session = Depends(get_db),
):
    """ステータス更新"""
    return status_crud.update_status(db, status, status_data)


@router.delete("/{status_id}", status_code=204)
def delete_status(
    status: Status = Depends(get_status_or_404),
    db: Session = Depends(get_db),
):
    """ステータス削除"""
    if status_crud.has_tasks_with_status(db, status.id):
        raise HTTPException(
            status_code=409,
            detail="このステータスに紐付くタスクが存在するため削除できません",
        )
    status_crud.delete_status(db, status)
