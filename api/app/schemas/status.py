from datetime import datetime

from pydantic import BaseModel, Field


class StatusBase(BaseModel):
    """ステータスの共通フィールド"""
    name: str = Field(..., min_length=1, max_length=50)
    color: str = Field(..., max_length=7)


class StatusCreate(StatusBase):
    """ステータス作成用スキーマ"""
    pass


class StatusUpdate(StatusBase):
    """ステータス更新用スキーマ"""
    pass


class StatusReorder(BaseModel):
    """ステータス並び替え用スキーマ"""
    order: list[int] = Field(..., min_length=1, description="並び順のステータスIDリスト")


class StatusResponse(StatusBase):
    """ステータスレスポンス用スキーマ"""
    id: int
    order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class StatusListResponse(BaseModel):
    """ステータス一覧レスポンス用スキーマ"""
    statuses: list[StatusResponse]
