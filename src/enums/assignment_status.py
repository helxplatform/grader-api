from enum import Enum

class AssignmentStatus(str, Enum):
    UNPUBLISHED = 'UNPUBLISHED'
    UPCOMING    = 'UPCOMING'
    OPEN        = 'OPEN'
    CLOSED      = 'CLOSED'