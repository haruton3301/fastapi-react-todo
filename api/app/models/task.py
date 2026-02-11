from sqlalchemy import Column, ForeignKey, Integer, String, Text, Date

from app.database import Base
from app.models.base import TimestampMixin


class Task(TimestampMixin, Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    due_date = Column(Date, nullable=False, index=True)
    status_id = Column(Integer, ForeignKey("statuses.id"), nullable=False)
