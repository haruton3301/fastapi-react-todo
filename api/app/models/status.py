from sqlalchemy import Column, Integer, String

from app.database import Base
from app.models.base import TimestampMixin


class Status(TimestampMixin, Base):
    __tablename__ = "statuses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    color = Column(String(7), nullable=False)
    order = Column(Integer, nullable=False, index=True)
