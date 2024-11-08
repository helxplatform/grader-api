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
    resource_type: ResourceType.COURSE
    resource: CourseModel

class UserCrudEvent(CrudEvent):
    resource_type: ResourceType.USER
    resource: UserModel

class AssignmentCrudEvent(CrudEvent):
    resource_type: ResourceType.ASSIGNMENT
    resource: AssignmentModel

class SubmissionCrudEvent(CrudEvent):
    resource_type: ResourceType.SUBMISSION
    resource: SubmissionModel