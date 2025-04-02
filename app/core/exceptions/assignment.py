from .base import CustomException

class AssignmentDueBeforeOpenException(CustomException):
    code = 400
    error_code = "ASSIGNMENT__DUE_BEFORE_OPEN"
    message = "assignment cannot be due before it has opened"

class AssignmentNotOpenException(CustomException):
    code = 403
    error_code = "ASSIGNMENT__NOT_OPEN"
    message = "assignment not open to student yet"

class AssignmentClosedException(CustomException):
    code = 403
    error_code = "ASSIGNMENT__CLOSED"
    message = "assignment closed for student"

class AssignmentNotCreatedException(CustomException):
    code = 403
    error_code = "ASSIGNMENT__NOT_CREATED"
    message = "assignment not created"

class AssignmentNotPublishedException(CustomException):
    code = 403
    error_code = "ASSIGNMENT__NOT_PUBLISHED"
    message = "assignment not published"

class AssignmentNotFoundException(CustomException):
    code = 404
    error_code = "ASSIGNMENT__NOT_FOUND"
    message = "assignment not found"

class AssignmentCannotBeUnpublished(CustomException):
    code = 400
    error_code = "ASSIGNMENT__CANNOT_BE_UNPUBLISHED"
    message = "assignment cannot be unpublished"

class AssignmentNotebookRevisionNotFoundException(CustomException):
    code = 404
    error_code = "ASSIGNMENT__NOTEBOOK_REVISION_NOT_FOUND"
    message = "master notebook revision not found"

class AssignmentNotebookRevisionNotSelectedException(AssignmentNotebookRevisionNotFoundException):
    """ An assignment begins with no master notebook. This is up to the professor to create and select. """
    message = "a master notebook has not been selected for the assignment yet"

class AssignmentNotebookRevisionCommittedException(CustomException):
    code = 409
    error_code = "ASSIGNMENT__NOTEBOOK_REVISION_COMMITTED"
    message = "the notebook revision has been committed and its contents are now immutable"