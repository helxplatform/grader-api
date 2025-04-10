from .base import CustomException

class AssignmentOverrideNotFoundException(CustomException):
    code = 404
    error_code = "ASSIGNMENT_OVERRIDE__NOT_FOUND"
    message = "assignment override not found"