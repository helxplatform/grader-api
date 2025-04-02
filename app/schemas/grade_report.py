from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from app.models import SubmissionModel

class GradeReportSchema(BaseModel):
    id: int
    average: float
    median: float
    minimum: float
    maximum: float
    stdev: float
    scores: list[float]
    total_points: float
    num_submitted: int
    # num_skipped = num_submitted (== num students w/ submissions) - num_active_submissions_already_graded
    num_skipped: int

    master_notebook_content: str
    otter_config_content: str
    
    created_date: datetime

    assignment_id: int

    class Config:
        orm_mode = True

class SubmissionGradeSchema(BaseModel):
    score: float
    total_points: float
    comments: Optional[str]
    submission_already_graded: bool = False

""" By identifying the submission, the associated student and assignment can also be identified. """
class IdentifiableSubmissionGradeSchema(SubmissionGradeSchema):
    submission: SubmissionModel

    class Config:
        arbitrary_types_allowed = True