from enum import Enum

class CanvasEnrollmentType(str, Enum):
    STUDENT     = 'student'
    TEACHER     = 'teacher'
    TA          = 'ta'
    DESIGNER    = 'designer'
    OBSERVER    = 'observer'