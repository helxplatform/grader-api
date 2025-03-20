from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models import CourseModel, InstructorModel
from src.services import CourseService
from src.schemas import CourseWithInstructorsSchema
from src.core.dependencies import get_db, PermissionDependency, CourseListPermission, InstructorListPermission

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
