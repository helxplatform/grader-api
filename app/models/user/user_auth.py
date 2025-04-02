from sqlalchemy import Column, String, Text, ForeignKey
from app.database import Base

class AutoPasswordAuthModel(Base):
    __tablename__ = "user_auto_password_auth"
    onyen = Column(String, ForeignKey("user_account.onyen"), primary_key=True)
    autogen_password_hash = Column(Text, nullable=False)
    