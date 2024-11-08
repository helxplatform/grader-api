from pydantic import BaseModel
from .websocket import WebsocketMessage

# At the moment. we have no fields defined for a generalized pubsub message.
# You can encode any JSON-serializable schema. I've defined it as such in case
# we need to define additional fields for general pubsub messages in the future.
PubsubMessage = BaseModel

""" This is a specialized type of PubSub message used to encapsulate a websocket message to send to a set of users. """
class PubsubWSMessage(PubsubMessage):
    user_ids: list[int]
    websocket_message: WebsocketMessage