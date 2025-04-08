from typing import List
from pydantic import BaseModel
from uuid import UUID
from fastapi import APIRouter, Request, Depends, UploadFile, File
from sqlalchemy.orm import Session
from app.celery.tasks import downsync_task
from app.services import LmsSyncService, AssignmentService, JobStatusService
from app.schemas import JobSchema
from app.core.dependencies import (
    get_db, PermissionDependency,
    UserIsInstructorPermission
)

router = APIRouter()

class GradeUpload(BaseModel):
    onyen: str
    percent_correct: int

class UploadGradesBody(BaseModel):
    grades: List[GradeUpload]

@router.post("/lms/downsync", response_model=JobSchema)
async def downsync(
    *,
    db: Session = Depends(get_db),
    perm: None = Depends(PermissionDependency(UserIsInstructorPermission))
):
    task = downsync_task.delay()
    return JobSchema.from_async_result(task)

@router.get("/lms/downsync/status", response_model=JobSchema | None)
async def get_downsync_job(
    *,
    db: Session = Depends(get_db),
    perm: None = Depends(PermissionDependency(UserIsInstructorPermission))
):
    status = JobStatusService(db).get_singleton_job_status(downsync_task)
    if status is None: return None
    return JobSchema.from_orm(status)