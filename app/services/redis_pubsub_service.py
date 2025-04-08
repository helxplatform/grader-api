import json
import redis
from app.database import redis_general_async_client, redis_general_client
from app.schemas import PubsubMessage

""" A particular instance of this service can be used to subscribe to different sets of channels.
You do not need to construct an instance of the service to publish a message to a channel. """
class RedisPubsubService:
    def __init__(self):
        self.pubsub = redis_general_async_client.pubsub()

    async def subscribe(self, channels: list[str] | str) -> redis.client.PubSub:
        if isinstance(channels, str): channels = [channels]

        await self.pubsub.subscribe(*channels)
        return self.pubsub

    async def unsubscribe(self, channels: list[str] | str) -> None:
        if isinstance(channels, str): channels = [channels]

        await self.pubsub.unsubscribe(*channels)

    @staticmethod
    async def publish(channel: str, message: PubsubMessage) -> None:
        serialized_message = message.json()
        await redis_general_async_client.publish(channel, serialized_message)

    @staticmethod
    def publish_sync(channel: str, message: PubsubMessage) -> None:
        serialized_message = message.json()
        redis_general_client.publish(channel, serialized_message)
