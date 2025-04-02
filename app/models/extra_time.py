from sqlalchemy import (
    Column, Sequence, ForeignKey,
    Integer, Interval,
)
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.orm import relationship, backref
from app.database import Base

class ExtraTimeModel(Base):
    __tablename__ = "extra_time"

    id = Column(Integer, Sequence("extra_time_id_seq"), primary_key=True, autoincrement=True, index=True)
    
    deferred_time = Column(Interval, server_default="0")
    extra_time = Column(Interval, server_default="0")

    student_id = Column(Integer, ForeignKey("student.id"), nullable=False)
    assignment_id = Column(Integer, ForeignKey("assignment.id"), nullable=False)

    student = relationship("StudentModel", foreign_keys="ExtraTimeModel.student_id", back_populates="extra_times")
    assignment = relationship(
        "AssignmentModel",
        foreign_keys="ExtraTimeModel.assignment_id",
        backref=backref("extra_times", cascade="all,delete")
    )

    # Ensures multiple extra_time rows can't exist with the same student_id AND assignment_id.
    __table_args__ = (UniqueConstraint("student_id", "assignment_id"),)