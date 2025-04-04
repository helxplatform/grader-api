from pathlib import Path
from sqlalchemy import (
    Column, Sequence, Boolean,
    Integer, Text, DateTime,
    func, ForeignKey
)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.hybrid import hybrid_property
from app.database import Base

class AssignmentModel(Base):
    __tablename__ = "assignment"

    id = Column(Integer, Sequence("assignment_id_seq"), primary_key=True, index=True)
    name = Column(Text, nullable=False, unique=True)
    directory_path = Column(Text, nullable=False)
    grader_question_feedback = Column(Boolean, server_default='t', nullable=False)
    max_attempts = Column(Integer, nullable=True)
    created_date = Column(DateTime(timezone=True), server_default=func.current_timestamp())
    available_date = Column(DateTime(timezone=True))
    due_date = Column(DateTime(timezone=True))
    last_modified_date = Column(DateTime(timezone=True), server_default=func.current_timestamp())
    is_published = Column(Boolean, server_default='f', nullable=False)
    manual_grading = Column(Boolean, server_default='f', nullable=False)

    # An assignment does not necessarily have a master notebook until the professor
    # creates one.
    master_notebook_revision_id = Column(Integer, ForeignKey("master_notebook_revision.id"), nullable=True)
    master_notebook_revisions = relationship(
        "MasterNotebookRevisionModel",
        backref=backref("assignments", cascade="all,delete"),
        foreign_keys="MasterNotebookRevisionModel.assignment_id"
    )
    active_master_notebook_revision = relationship(
        "MasterNotebookRevisionModel",
        uselist=False,
        backref=None,
        foreign_keys=[master_notebook_revision_id]
    )

    @hybrid_property
    def master_notebook_path(self) -> str | None:
        if self.active_master_notebook_revision is None: return None
        return self.active_master_notebook_revision.master_notebook_path

    @hybrid_property
    def student_notebook_path(self) -> str | None:
        if self.active_master_notebook_revision is None: return None

        if self.manual_grading:
            # If the assignment is manually graded, there is no distinct "student" version.
            # They just share the same notebook.
            return self.master_notebook_path
        
        return self.active_master_notebook_revision.student_notebook_path
        