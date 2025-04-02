from .base import CustomException

class AppstoreUserNotFoundException(CustomException):
    code = 404
    error_code = "APPSTORE__USER_NOT_FOUND"
    message = "appstore user not found"

class AppstoreUserDoesNotMatchException(CustomException):
    code = 403
    error_code = "APPSTORE__USER_DOES_NOT_MATCH"
    message = "appstore user does not have an associated eduhelx account"

class AppstoreUnsupportedUserTypeException(CustomException):
    code = 403
    error_code = "APPSTORE__USER_TYPE_UNSUPPORTED"
    message = "appstore does not support this type of user"