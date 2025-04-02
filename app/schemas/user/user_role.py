from typing import List
from pydantic import BaseModel
from .user_permission import UserPermissionSchema

class UserRoleSchema(BaseModel):
    name: str
    permissions: List[UserPermissionSchema]