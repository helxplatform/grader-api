from __future__ import annotations
from sqlalchemy import Column, Sequence, Integer, Text, DateTime
from app.database import Base

class CourseModel(Base):
    __tablename__ = "course"

    id = Column(Integer, Sequence("course_id_seq"), primary_key=True, index=True)
    name = Column(Text, nullable=False)
    start_at = Column(DateTime(timezone=True), nullable=True)
    end_at = Column(DateTime(timezone=True), nullable=True)
    master_remote_url = Column(Text, nullable=False)