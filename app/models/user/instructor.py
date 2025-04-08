from sqlalchemy import Column, Integer, ForeignKey
from .user import UserModel, UserType

class InstructorModel(UserModel):
    __tablename__ = "instructor"
    __mapper_args__ = {"polymorphic_identity": UserType.INSTRUCTOR}
    id = Column(Integer, ForeignKey("user_account.id"), primary_key=True)

    