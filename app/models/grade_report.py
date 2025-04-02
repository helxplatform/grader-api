from __future__ import annotations
from sqlalchemy import Column, Sequence, ForeignKey, Integer, Float, DateTime, ARRAY, Text, func
from sqlalchemy.orm import relationship, backref
from app.database import Base
from app.models.assignment import AssignmentModel
from app.schemas.grade_report import SubmissionGradeSchema
import numpy as np

class GradeReportModel(Base):
    __tablename__ = "grade_report"

    id = Column(Integer, Sequence("grade_report_id_seq"), primary_key=True, autoincrement=True, index=True)
    average = Column(Float, nullable=False)
    median = Column(Float, nullable=False)
    minimum = Column(Float, nullable=False)
    maximum = Column(Float, nullable=False)
    stdev = Column(Float, nullable=False)
    scores = Column(ARRAY(Float), nullable=False)
    total_points = Column(Float, nullable=False)
    num_skipped = Column(Integer, nullable=False)
    num_submitted = Column(Integer, nullable=False)

    master_notebook_content = Column(Text, nullable=False)
    otter_config_content = Column(Text, nullable=False)

    created_date = Column(DateTime(timezone=True), nullable=False, server_default=func.current_timestamp())

    assignment_id = Column(Integer, ForeignKey("assignment.id"), nullable=False)
    assignment = relationship(
        "AssignmentModel",
        foreign_keys="GradeReportModel.assignment_id",
        backref=backref("grade_reports", cascade="all,delete")
    )

    @staticmethod
    def from_submission_grades(
        assignment: AssignmentModel,
        submission_grades: list[SubmissionGradeSchema],
        master_notebook_content: str,
        otter_config_content: str
    ) -> GradeReportModel:
        scores = [grade.score for grade in submission_grades]
        average = float(np.mean(scores))
        median = float(np.median(scores))
        stdev = float(np.std(scores))
        minimum, maximum = min(scores), max(scores)
        num_submitted = len(submission_grades)
        num_skipped = sum([grade.submission_already_graded for grade in submission_grades])
        
        return GradeReportModel(
            average=average,
            median=median,
            minimum=minimum,
            maximum=maximum,
            stdev=stdev,
            scores=scores,
            total_points=submission_grades[0].total_points,
            num_submitted=num_submitted,
            num_skipped=num_skipped,
            master_notebook_content=master_notebook_content,
            otter_config_content=otter_config_content,
            assignment_id=assignment.id
        )