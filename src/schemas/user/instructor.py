from datetime import datetime
from .user import UserSchema

class InstructorSchema(UserSchema):
    class Config:
        orm_mode = True