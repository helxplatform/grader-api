from sqlalchemy import Column, ForeignKey, String

from app.database import Base


class OnyenPIDModel(Base):
    __tablename__ = "user_onyen_pid"
    onyen = Column(String, ForeignKey("user_account.onyen"), primary_key=True, nullable=False, unique=True)
    pid = Column(String, nullable=False, unique=True)