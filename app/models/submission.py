from sqlalchemy import (
    Column, Sequence, ForeignKey,
    Integer, String, DateTime,
    Boolean, func
)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.hybrid import hybrid_property
from app.database import Base

class SubmissionModel(Base):
    __tablename__ = "submission"

    id = Column(Integer, Sequence("submission_id_seq"), primary_key=True, autoincrement=True, index=True)
    student_id = Column(Integer, ForeignKey("student.id"), nullable=False)
    assignment_id = Column(Integer, ForeignKey("assignment.id"), nullable=False)
    master_notebook_revision_id = Column(Integer, ForeignKey("master_notebook_revision.id"))

    commit_id = Column(String(255), nullable=False)
    graded = Column(Boolean(), server_default="f", nullable=False)
    submission_time = Column(DateTime(timezone=True), server_default=func.current_timestamp())

    student = relationship("StudentModel", foreign_keys="SubmissionModel.student_id", back_populates="submissions")
    assignment = relationship(
        "AssignmentModel",
        foreign_keys="SubmissionModel.assignment_id",
        backref=backref("submissions", cascade="all,delete")
    )
    master_notebook_revision = relationship(
        "MasterNotebookRevisionModel",
        foreign_keys="SubmissionModel.master_notebook_revision_id",
        # Master notebook revisions should never be deleted except if the assignment itself is,
        # so we should not cascade delete submissions here.
        # (Assignment deletion will cascade delete both the submission and all its notebook revisions).
        backref=backref("submissions")
    )

    @hybrid_property
    def associated_with_active_revision(self) -> bool:
        active_notebook_revision = self.assignment.active_master_notebook_revision
        if active_notebook_revision is None:
            # There should be no way to create a submission in such a scenario.
            # The submission service asks the assignment service to validate this, and you
            # can't update the assignment once it has a revision to no longer have one.
            # Regardless, good to include a check.
            return False
        return self.master_notebook_revision_id == active_notebook_revision.id
