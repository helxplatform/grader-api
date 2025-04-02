from .base import ForbiddenException
from app.core.role_permissions import UserPermission

class MissingPermissionException(ForbiddenException):
    code = 403
    error_code = "AUTH__MISSING_PERMISSION"

    def __init__(self, permission: UserPermission):
        super().__init__(
            message=f'You do not have the permission "{ permission.value }"'
        )