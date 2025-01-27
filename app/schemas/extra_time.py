from datetime import datetime, timedelta

from pydantic import BaseModel

from .assignment import AssignmentSchema
from .user import StudentSchema


class ExtraTimeSchema(BaseModel):
    id: int
    extra_time: timedelta
    deferred_date: datetime
    student: StudentSchema
    assignment: AssignmentSchema

    class Config:
        orm_mode = True