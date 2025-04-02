from enum import Enum

class CanvasWorkflowStateFilter(str, Enum):
    SUBMITTED      = 'submitted'
    UNSUBMITTED    = 'unsubmitted'
    GRADED         = 'graded'
    PENDING_REVIEW = 'pending_review'