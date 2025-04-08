from __future__ import annotations
from typing import Any
from pydantic import BaseModel
from enum import Enum
from uuid import UUID
from datetime import datetime
from dateutil import parser as dateparser
from celery.result import AsyncResult
from app.models.job_status import JobStatus

class JobSchema(BaseModel):
    """ A pending status may imply the job is unknown or does not exist. """
    id: UUID
    type: str | None
    status: JobStatus

    @classmethod
    def from_async_result(cls, result: AsyncResult) -> JobSchema:
        return cls(
            id=result.task_id,
            name=result.name,
            status=JobStatus[result.status]
        )
    
    class Config:
        orm_mode = True

class JobResultSchema(JobSchema):
    result: Any
    ready: bool
    successful: bool
    failed: bool
    # Task metadata, not necessarily defined (e.g., when in reserved state)
    queue: str | None
    retries: int | None
    traceback: str | None
    finished_date: datetime | None

    @classmethod
    def from_async_result(cls, result: AsyncResult) -> JobResultSchema:
        return cls(
            **JobSchema.from_async_result(result).dict(),
            result=result.result,
            ready=result.ready(),
            successful=result.successful(),
            failed=result.failed(),
            queue=result.queue,
            retries=result.retries,
            traceback=result.traceback,
            finished_date=result.date_done
        )