from enum import Enum
from pydantic import BaseModel
from fastapi_events.registry.payload_schema import registry

class SyncEvents(Enum):
    SYNC_CREATE_ASSIGNMENT = "SYNC_CREATE_ASSIGNMENT"

@registry.register
class SyncCreateAssignmentEvent(BaseModel):
    __event_name__ = SyncEvents.SYNC_CREATE_ASSIGNMENT
    
    assignment_id: int