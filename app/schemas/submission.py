from datetime import datetime
from pydantic import BaseModel


class DatabaseSubmissionSchema(BaseModel):
    id: int
    commit_id: str
    graded: bool
    submission_time: datetime

    class Config:
        orm_mode = True

class SubmissionSchema(DatabaseSubmissionSchema):
    active: bool