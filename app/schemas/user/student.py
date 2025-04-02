from datetime import datetime
from .user import UserSchema

class StudentSchema(UserSchema):
    fork_remote_url: str
    fork_cloned: bool
    join_date: datetime
    exit_date: datetime | None