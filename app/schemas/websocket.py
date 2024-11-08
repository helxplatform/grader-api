from __future__ import annotations
from typing import Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from app.schemas.events import CrudEvent, CrudType, ResourceType

# General definition for an emittable websocket message
class WebsocketMessage(BaseModel):
    event_name: str
    uuid: UUID = Field(default_factory=uuid4)
    # If the message is in response to another.
    originator: Optional[UUID]
    data: Optional[BaseModel]

# General definition for an emittable websocket message indicating an error of some kind
class WebsocketErrorMessage(WebsocketMessage):
    exception: Exception

    class Config:
        arbitrary_types_allowed = True


class CrudPayload(BaseModel):
    crud_type: CrudType
    resource_type: ResourceType
    resource_id: int

    @classmethod
    def from_crud_event(cls, crud_event: CrudEvent, resource_id: int) -> CrudPayload:
        return cls(
            crud_type=crud_event.crud_type,
            resource_type=crud_event.resource_type,
            resource_id=resource_id
        )

class WebsocketCrudMessage(WebsocketMessage):
    event_name = "crud_event"
    data: CrudPayload

    @classmethod
    def from_crud_event(cls, crud_event: CrudEvent, resource_id: int) -> WebsocketCrudMessage:
        return cls(data=CrudPayload.from_crud_event(crud_event, resource_id))