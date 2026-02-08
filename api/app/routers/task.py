from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.crud import task as task_crud
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskListResponse

router = APIRouter(prefix="/tasks", tags=["tasks"])


def get_task_or_404(
    task_id: int,
    db: Session = Depends(get_db),
) -> Task:
    """タスク取得（存在しない場合は404）"""
    task = task_crud.get_task(db, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.get("", response_model=TaskListResponse)
def list_tasks(
    order: str = Query(default="desc", regex="^(asc|desc)$"),
    db: Session = Depends(get_db),
):
    """タスク一覧取得（締切日でソート）"""
    tasks = task_crud.get_tasks(db, order=order)
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
    db: Session = Depends(get_db),
):
    """タスク作成"""
    return task_crud.create_task(db, task_data)


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_data: TaskUpdate,
    task: Task = Depends(get_task_or_404),
    db: Session = Depends(get_db),
):
    """タスク更新"""
    return task_crud.update_task(db, task, task_data)


@router.delete("/{task_id}", status_code=204)
def delete_task(
    task: Task = Depends(get_task_or_404),
    db: Session = Depends(get_db),
):
    """タスク削除"""
    task_crud.delete_task(db, task)
