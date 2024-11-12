import json
from typing import Iterable
from fastapi import WebSocket
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from app.services import RedisPubsubService
from app.models.user import UserModel, UserType
from app.schemas import WebsocketMessage, WebsocketErrorMessage, PubsubWSMessage

PUBSUB_WS_CHANNEL = "websocket_messages"

""" A couple notes:
- A particular user may be connected to a websocket on a separate instance of the API, depending on if replicas are enabled.
This means that consistency across replicas is important, hence the pubsub architecture.
- A particular user might maintain multiple connections to the server (e.g., if they have multiple tabs of Jupyter open),
so it is important that any event for a particular user gets relayed to each of their associated clients.

Thus, the usage of this service may be misleading. You should not be directly emitting websocket messages to users or clients,
unless you have good reason to. In general, websocket events should be dispatched via pubsub (`publish_pubsub_ws_message`).
"""
class WebsocketManagerService:
    _clients = []
    _pubsub_service = RedisPubsubService()

    def __init__(self, session: Session):
        self.session = session

    async def handle_client_message(self, client: WebSocket):
        """ SINCE WE DO NOT USE CLIENT -> SERVER MESSAGING YET, THIS FUNCTIONALITY IS NOT FLESHED OUT. """
        """ Might move this to a separate area of the code. """
        # If a client sends invalid JSON in the payload, it will close the connection.
        data = await client.receive_json()
        event_name = data["event_name"]

        # Do something with the event...

    @classmethod
    async def connect(cls, client: WebSocket):
        """ Connect an incoming WebSocket connection to the server """
        await client.accept()
        cls._clients.append(client)

    @classmethod
    async def disconnect(cls, client: WebSocket):
        """ Disconnect a client/connection from the server """
        cls._clients.remove(client)

    @classmethod
    def _get_connections_for_id(cls, id: int) -> list[WebSocket]:
        """ Get active websocket connections associated with a user's id. """
        return [
            client for client in cls._clients
            if client.user.id == id
        ]

    @classmethod
    def _get_connections_for_onyen(cls, onyen: str) -> list[WebSocket]:
        """ Get active websocket connections associated with a user's onyen. """
        return [
            client for client in cls._clients
            if client.user.onyen == onyen
        ]
    
    @classmethod
    async def _send_raw_message_to_client(cls, websocket: WebSocket, message: dict):
        """ Send a raw message to an individual websocket connection.
        `message` should be deserializable to WebsocketMessage.
        """
        await websocket.send_json(jsonable_encoder(message))

    @classmethod
    async def receive_pubsub_ws_messages(cls):
        """ Subscribe to the PubSub channel for relaying WS messages and emit the message to clients.
        This is intended to be run as a background task (see: `asyncio.create_task`). """
        await cls._pubsub_service.subscribe(PUBSUB_WS_CHANNEL)
        try:
            while True:
                # We use a shorter timeout here so that app shutdown is more efficient.
                message = await cls._pubsub_service.pubsub.get_message(timeout=2.5, ignore_subscribe_messages=True)
                if message is not None:
                    channel = message["channel"]
                    ps_data = json.loads(message["data"].decode("utf-8"))
                    user_ids = ps_data["user_ids"]
                    data = ps_data["websocket_message"]

                    clients = set()
                    # Find all clients of users the message is intended for.
                    for user_id in user_ids: clients.update(cls._get_connections_for_id(user_id))

                    # Emit encapsulated websocket message to clients.
                    # print("----EMITTING WS MESSAGE TO CLIENTS----")
                    # print("DATA:", data)
                    # print("CLIENTS:", user_ids)
                    # print("CLIENT LIST:", clients)
                    for client in clients: await cls._send_raw_message_to_client(client, data)
        finally:
            await cls._pubsub_service.unsubscribe(PUBSUB_WS_CHANNEL)

    @staticmethod
    async def publish_pubsub_ws_message(websocket_message: WebsocketMessage, users: Iterable[UserModel]):
        """ Publish a pubsub event encapsulating a websocket event to emit to clients. """
        ps_message = PubsubWSMessage(
            websocket_message=websocket_message,
            user_ids=[u.id for u in users]
        )
        await RedisPubsubService.publish(PUBSUB_WS_CHANNEL, ps_message)

    @staticmethod
    def publish_sync_pubsub_ws_message(websocket_message: WebsocketMessage, users: Iterable[UserModel]):
        """ Synchronously publish a pubsub event encapsulating a websocket event to emit to clients.
        Pubsub channels cannot be published to asynchronously from Celery workers.
        """
        ps_message = PubsubWSMessage(
            websocket_message=websocket_message,
            user_ids=[u.id for u in users]
        )
        RedisPubsubService.publish_sync(PUBSUB_WS_CHANNEL, ps_message)