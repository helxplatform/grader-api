from typing import List
from pydantic import BaseModel
from uuid import UUID
from fastapi import APIRouter, Request, Depends, UploadFile, File
from sqlalchemy.orm import Session
from app.celery import get_task_result_by_id
from app.celery.tasks import downsync_task
from app.services import LmsSyncService, AssignmentService
from app.schemas import JobSchema, JobResultSchema
from app.core.dependencies import (
    get_db, PermissionDependency,
    UserIsInstructorPermission
)

router = APIRouter()

@router.get("/jobs/{id}", response_model=JobResultSchema)
async def get_job(
    *,
    id: UUID,
    perm: None = Depends(PermissionDependency(UserIsInstructorPermission))
):
    """
    NOTE: Task ID is not validated. A pending task does not necessarily exist;
    this state is returned by default for unknown task ids.
    """
    return JobResultSchema.from_async_result(get_task_result_by_id(str(id)))

@router.get("/jobs/{id}/status", response_model=JobSchema)
async def get_job(
    *,
    id: UUID,
    perm: None = Depends(PermissionDependency(UserIsInstructorPermission))
):
    """
    NOTE: Task ID is not validated. A pending task does not necessarily exist;
    this state is returned by default for unknown task ids.
    """
    return JobSchema.from_async_result(get_task_result_by_id(str(id)))