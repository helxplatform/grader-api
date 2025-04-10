from sqlalchemy import (
    Column, Sequence, ForeignKey,
    Integer, Interval, DateTime
)
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.orm import relationship, backref
from app.database import Base

class AssignmentOverrideModel(Base):
    __tablename__ = "assignment_override"

    id = Column(Integer, primary_key=True, index=True)

    student_id = Column(Integer, ForeignKey("student.id"), nullable=False)
    assignment_id = Column(Integer, ForeignKey("assignment.id"), nullable=False)

    due_date = Column(DateTime(timezone=True))
    available_date = Column(DateTime(timezone=True))

    student = relationship(
        "StudentModel",
        foreign_keys="AssignmentOverrideModel.student_id",
        backref=backref("assignment_overrides", cascade="all,delete")
    )
    assignment = relationship(
        "AssignmentModel",
        foreign_keys="AssignmentOverrideModel.assignment_id",
        backref=backref("assignment_overrides", cascade="all,delete")
    )