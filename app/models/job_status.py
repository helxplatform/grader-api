from __future__ import annotations
from sqlalchemy import Column, Sequence, Integer, Text, DateTime, Enum, func
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
import enum

class JobStatus(str, enum.Enum):
    """ Pending may indicate an unknown or nonexistent task. """
    PENDING = "pending"
    RECEIVED = "received"
    STARTED = "started"
    RETRY = "retry"
    FAILURE = "failure"
    SUCCESS = "success"
    REVOKED = "revoked"

class JobStatusModel(Base):
    __tablename__ = "job_status"

    internal_id = Column(Integer, Sequence("job_status_internal_id_seq"), primary_key=True, index=True)
    id = Column(UUID(as_uuid=True), nullable=False, unique=False)
    status = Column(Enum(JobStatus), nullable=False)
    type = Column(Text, nullable=True)
    status_date = Column(DateTime(timezone=True), server_default=func.current_timestamp())