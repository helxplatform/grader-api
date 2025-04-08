from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import CourseModel, InstructorModel
from app.services import CourseService
from app.schemas import CourseWithInstructorsSchema
from app.core.dependencies import get_db, PermissionDependency, CourseListPermission, InstructorListPermission

router = APIRouter()

@router.get("/course", response_model=CourseWithInstructorsSchema)
async def get_course(
    *,
    db: Session = Depends(get_db),
    perm: None = Depends(PermissionDependency(CourseListPermission, InstructorListPermission)),
    request: Request
):
    # request.app.logger.info("get_course")
    return await CourseService(db).get_course_with_instructors_schema()
