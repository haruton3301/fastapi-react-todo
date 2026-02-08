from datetime import datetime

from sqlalchemy import Column, DateTime
from sqlalchemy.sql import func


class TimestampMixin:
    """created_at, updated_at を提供するMixin"""
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )
