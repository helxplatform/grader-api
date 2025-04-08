from pydantic import BaseModel

class UserPermissionSchema(BaseModel):
    name: str