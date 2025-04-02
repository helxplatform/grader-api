from pathlib import Path
from sqlalchemy import (
    Column, Sequence, Boolean,
    Integer, Text, DateTime,
    func, ForeignKey
)
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.hybrid import hybrid_property
from app.database import Base

class MasterNotebookRevisionModel(Base):
    __tablename__ = "master_notebook_revision"

    id = Column(Integer, Sequence("master_notebook_revision_id_seq"), primary_key=True, index=True)
    # Relative to the assignment root (assignment.directory_path), i.e., the fully qualified path
    # of the file within the repo is `/{directory_path}/{master_notebook_path}`
    master_notebook_path = Column(Text, nullable=False)
    master_notebook_content = Column(Text, nullable=False)
    created_date = Column(DateTime(timezone=True), server_default=func.current_timestamp())

    assignment_id = Column(Integer, ForeignKey("assignment.id"), nullable=False)
    
    # Ensures that no assignment can have multiple revisions associated with the same notebook file.
    __table_args__ = (UniqueConstraint("master_notebook_path", "assignment_id"),)

    @hybrid_property
    def student_notebook_path(self) -> str:
        """ NOTE: a manually graded assignment may not actually have a student notebook path. """
        p = Path(self.master_notebook_path)
        return str(p.parents[0] / (p.stem + "-student.ipynb"))