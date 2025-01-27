from typing import List

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.dependencies import (InstructorCreatePermission,
                                   InstructorListPermission,
                                   PermissionDependency, get_db)
from app.schemas import InstructorSchema
from app.services import InstructorService

router = APIRouter()

class CreateInstructorBody(BaseModel):
    onyen: str
    first_name: str
    last_name: str
    email: str

@router.get("/instructors/{onyen:str}", response_model=InstructorSchema)
async def get_instructor(
    *,
    db: Session = Depends(get_db),
    perm: None = Depends(PermissionDependency(InstructorListPermission)),
    onyen: str
):
    instructor = await InstructorService(db).get_user_by_onyen(onyen)
    return instructor

@router.get("/instructors", response_model=List[InstructorSchema])
async def list_instructor(
    *,
    db: Session = Depends(get_db),
    perm: None = Depends(PermissionDependency(InstructorListPermission))
):
    instructors = await InstructorService(db).list_instructors()
    return instructors

@router.post("/instructors", response_model=InstructorSchema)
async def create_instructor_without_password(
    *,
    db: Session = Depends(get_db),
    perm: None = Depends(PermissionDependency(InstructorCreatePermission)),
    instructor_body: CreateInstructorBody
):
    instructor = await InstructorService(db).create_instructor(
        **instructor_body.dict()
    )
    return instructor