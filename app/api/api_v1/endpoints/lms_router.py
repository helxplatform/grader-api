from typing import List
from pydantic import BaseModel
from fastapi import APIRouter, Request, Depends, UploadFile, File
from sqlalchemy.orm import Session
from app.services import LmsSyncService, AssignmentService
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

@router.post("/lms/downsync")
async def downsync(
    *,
    db: Session = Depends(get_db),
    perm: None = Depends(PermissionDependency(UserIsInstructorPermission))
):
    await LmsSyncService(db).downsync()

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