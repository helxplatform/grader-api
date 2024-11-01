from __future__ import annotations
from typing import Any
from pydantic import BaseModel
from enum import Enum
from uuid import UUID
from datetime import datetime
from dateutil import parser as dateparser
from celery.result import AsyncResult

class JobStatus(str, Enum):
    """ Pending may indicate an unknown or nonexistent task. """
    PENDING = "pending"
    RECEIVED = "received"
    STARTED = "started"
    RETRY = "retry"
    FAILURE = "failure"
    SUCCESS = "success"
    REVOKED = "revoked"

class JobSchema(BaseModel):
    """ A pending status may imply the job is unknown or does not exist. """
    id: UUID
    status: JobStatus

    @classmethod
    def from_async_result(cls, result: AsyncResult) -> JobSchema:
        return cls(
            id=result.task_id,
            status=JobStatus[result.status]
        )

class JobResultSchema(JobSchema):
    result: Any
    ready: bool
    successful: bool
    failed: bool
    # Task metadata, not necessarily defined (e.g., when in reserved state)
    name: str | None
    queue: str | None
    retries: int | None
    traceback: str | None
    finished_date: datetime | None

    @classmethod
    def from_async_result(cls, result: AsyncResult) -> JobResultSchema:
        return cls(
            **JobSchema.from_async_result(result).dict(),
            name=result.name,
            result=result.result,
            ready=result.ready(),
            successful=result.successful(),
            failed=result.failed(),
            queue=result.queue,
            retries=result.retries,
            traceback=result.traceback,
            finished_date=result.date_done
        )