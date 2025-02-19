from .base import CustomException

class OtterConfigViolationException(CustomException):
    code = 403
    error_code = "GRADING__OTTER_CONFIG_VIOLATION"
    message = "otterconfig is invalid or cannot be generated for the assignment"

class AutogradingDisabledException(CustomException):
    code = 400
    error_code = "GRADING__AUTOGRADING_DISABLED"
    message = "autograding has been disabled for the assignment"

class StudentGradedMultipleTimesException(CustomException):
    code = 400
    error_code = "GRADING__STUDENT_GRADED_MULTIPLE_TIMES"
    message = "only 1 submission per student is permitted during grading"

class SubmissionMismatchException(CustomException):
    code = 400
    error_code = "GRADING__SUBMISSION_MISMATCH"
    message = "submission is not associated with the assignment being graded"