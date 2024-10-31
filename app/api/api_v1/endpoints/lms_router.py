from typing import List
from pydantic import BaseModel
from uuid import UUID
from fastapi import APIRouter, Request, Depends, UploadFile, File
from sqlalchemy.orm import Session
from app.celery.tasks import downsync_task
from app.services import LmsSyncService, AssignmentService
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

@router.post("/lms/downsync/students")
async def downsync_students(
    *,
    db: Session = Depends(get_db),
    perm: None = Depends(PermissionDependency(UserIsInstructorPermission))
):
    return await LmsSyncService(db).sync_students()

@router.post("/lms/downsync/assignments")
async def downsync_assignments(
    *,
    db: Session = Depends(get_db),
    perm: None = Depends(PermissionDependency(UserIsInstructorPermission))
):
    return await LmsSyncService(db).sync_assignments()