from datetime import datetime, timedelta
from pydantic import BaseModel
from .user import StudentSchema
from .assignment import AssignmentSchema

class ExtraTimeSchema(BaseModel):
    id: int
    extra_time: timedelta
    deferred_date: datetime
    student: StudentSchema
    assignment: AssignmentSchema

    class Config:
        orm_mode = True