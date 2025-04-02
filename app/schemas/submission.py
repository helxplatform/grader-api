from datetime import datetime
from pydantic import BaseModel
from .user import StudentSchema
from .assignment import AssignmentSchema

class DatabaseSubmissionSchema(BaseModel):
    id: int
    commit_id: str
    graded: bool
    submission_time: datetime
    # Whether or not the submission is associated with the active master notebook revision of the assignment.
    associated_with_active_revision: bool

    class Config:
        orm_mode = True

class SubmissionSchema(DatabaseSubmissionSchema):
    active: bool