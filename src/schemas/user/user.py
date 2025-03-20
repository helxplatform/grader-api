from pydantic import BaseModel
from src.models.user import UserType

class UserSchema(BaseModel):
    id: int
    user_type: UserType
    onyen: str
    name: str
    email: str

    class Config:
        orm_mode = True