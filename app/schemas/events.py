from pydantic import BaseModel
from enum import Enum
from app.models import CourseModel, AssignmentModel, SubmissionModel, UserModel
from app.models.user import UserType

class PydanticEvent(BaseModel):
    event_name: str
    
    class Config:
        arbitrary_types_allowed = True

class CrudType(str, Enum):
    CREATE = "CREATE"
    MODIFY = "MODIFY"
    DELETE = "DELETE"

class ResourceType(str, Enum):
    COURSE = "COURSE"
    USER = "USER"
    ASSIGNMENT = "ASSIGNMENT"
    SUBMISSION = "SUBMISSION"

class CrudEvent(PydanticEvent):
    event_name = "crud"
    crud_type: CrudType
    resource_type: ResourceType
    resource: AssignmentModel | SubmissionModel | UserModel | CourseModel
    modified_fields: list[str] | None = None

    class Config:
        arbitrary_types_allowed = True

class CourseCrudEvent(CrudEvent):
    resource: CourseModel
    resource_type = ResourceType.COURSE

class UserCrudEvent(CrudEvent):
    resource: UserModel
    resource_type = ResourceType.USER

class AssignmentCrudEvent(CrudEvent):
    resource: AssignmentModel
    resource_type = ResourceType.ASSIGNMENT

class SubmissionCrudEvent(CrudEvent):
    resource: SubmissionModel
    resource_type = ResourceType.SUBMISSION