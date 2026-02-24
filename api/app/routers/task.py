from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.crud import task as task_crud
from app.crud import status as status_crud
from app.models.task import Task
from app.models.user import User
from app.schemas.common import SortOrder
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskListResponse

router = APIRouter(prefix="/tasks", tags=["tasks"])


def get_task_or_404(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Task:
    """タスク取得（存在しない場合は404）"""
    task = task_crud.get_task(db, task_id, user_id=current_user.id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.get("", response_model=TaskListResponse)
def list_tasks(
    order: SortOrder = Query(default=SortOrder.desc),
    q: str | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """タスク一覧取得（締切日でソート）"""
    tasks = task_crud.get_tasks(db, user_id=current_user.id, order=order, keyword=q)
    return TaskListResponse(tasks=tasks)


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task: Task = Depends(get_task_or_404),
):
    """タスク詳細取得"""
    return task


@router.post("", response_model=TaskResponse, status_code=201)
def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """タスク作成"""
    # 存在しないステータス、または他ユーザーのステータスへの紐付けを防ぐ
    if status_crud.get_status(db, task_data.status_id, user_id=current_user.id) is None:
        raise HTTPException(status_code=404, detail="Status not found")
    return task_crud.create_task(db, task_data, user_id=current_user.id)


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_data: TaskUpdate,
    task: Task = Depends(get_task_or_404),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """タスク更新"""
    # 存在しないステータス、または他ユーザーのステータスへの紐付けを防ぐ
    if status_crud.get_status(db, task_data.status_id, user_id=current_user.id) is None:
        raise HTTPException(status_code=404, detail="Status not found")
    return task_crud.update_task(db, task, task_data)


@router.delete("/{task_id}", status_code=204)
def delete_task(
    task: Task = Depends(get_task_or_404),
    db: Session = Depends(get_db),
):
    """タスク削除"""
    task_crud.delete_task(db, task)
