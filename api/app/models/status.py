from sqlalchemy import Column, ForeignKey, Integer, String

from app.database import Base
from app.models.base import TimestampMixin


class Status(TimestampMixin, Base):
    __tablename__ = "statuses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    color = Column(String(7), nullable=False)
    order = Column(Integer, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
