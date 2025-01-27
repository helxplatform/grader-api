from enum import Enum

from fastapi_events.registry.payload_schema import registry
from pydantic import BaseModel


class SyncEvents(Enum):
    SYNC_CREATE_ASSIGNMENT = "SYNC_CREATE_ASSIGNMENT"

@registry.register
class SyncCreateAssignmentEvent(BaseModel):
    __event_name__ = SyncEvents.SYNC_CREATE_ASSIGNMENT
    
    assignment_id: int