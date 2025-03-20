from datetime import datetime
from pydantic import BaseModel, PositiveInt

from app.enums.assignment_status import AssignmentStatus
from ._unset import UNSET

class AssignmentOverrideSchema(BaseModel):
    id: int
    assignment_id: int
    student_id: int
    available_date: datetime
    due_date: datetime

    class Config:
        orm_mode = True
