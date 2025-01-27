from datetime import datetime
from typing import List

from pydantic import BaseModel

from ._unset import UNSET
from .user import InstructorSchema


class CourseSchema(BaseModel):
    id: int
    name: str
    start_at: datetime | None
    end_at: datetime | None
    master_remote_url: str

    class Config:
        orm_mode = True

class UpdateCourseSchema(BaseModel):
    name: str = UNSET
    master_remote_url: str = UNSET

class CourseWithInstructorsSchema(CourseSchema):
    instructors: List[InstructorSchema]