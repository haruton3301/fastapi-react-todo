from datetime import date, datetime

from pydantic import BaseModel, Field


class TaskBase(BaseModel):
    """タスクの共通フィールド"""
    title: str = Field(..., min_length=1, max_length=255)
    content: str
    due_date: date


class TaskCreate(TaskBase):
    """タスク作成用スキーマ"""
    pass


class TaskUpdate(TaskBase):
    """タスク更新用スキーマ"""
    pass


class TaskResponse(TaskBase):
    """タスクレスポンス用スキーマ"""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TaskListResponse(BaseModel):
    """タスク一覧レスポンス用スキーマ"""
    tasks: list[TaskResponse]
