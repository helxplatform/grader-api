from sqlalchemy import Column, Integer, Boolean, Interval, DateTime, Text, ForeignKey, func
from sqlalchemy.orm import relationship
from .user import UserModel, UserType

class StudentModel(UserModel):
    __tablename__ = "student"
    __mapper_args__ = {"polymorphic_identity": UserType.STUDENT}
    id = Column(Integer, ForeignKey("user_account.id"), primary_key=True)

    # This is just a flag to indicate that the student has cloned their fork,
    # which let's use deduce that if the directory doesn't exist, they've moved it.
    fork_remote_url = Column(Text)
    fork_cloned = Column(Boolean, server_default="0")
    base_extra_time = Column(Interval, server_default="0")
    join_date = Column(DateTime(timezone=True), server_default=func.current_timestamp())
    exit_date = Column(DateTime(timezone=True))

    submissions = relationship("SubmissionModel", cascade="all,delete", back_populates="student")
    extra_times = relationship("ExtraTimeModel", cascade="all,delete", back_populates="student")
    