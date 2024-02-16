import enum
import random
from dataclasses import dataclass
from typing import Optional

import pika

from dataclasses_avroschema import AvroModel


class FavoriteColor(enum.Enum):
    BLUE = "BLUE"
    YELLOW = "YELLOW"
    GREEN = "GREEN"


@dataclass
class UserModel(AvroModel):
    "An User"

    name: str
    age: int
    favorite_colors: FavoriteColor = FavoriteColor.BLUE
    country: str = "Argentina"
    address: Optional[str] = None

    class Meta:
        namespace = "User.v1"
        aliases = ["user-v1", "super user"]


def consume(*, channel, queue_name: str):
    def callback(channel: str, method, properties, body):
        print(f"Message received with body: {body} in channel {method} \n")
        user = UserModel.deserialize(body)
        print(f"Message deserialized: {user} \n")

    channel.basic_consume(on_message_callback=callback, queue=queue_name)
    channel.start_consuming()


def produce(*, channel, queue_name: str, total_events: int = 10):
    for event_number in range(1, total_events + 1):
        # Produce message
        print(f"Sending event number {event_number}")

        user = UserModel(
            name=random.choice(
                [
                    "Juan",
                    "Peter",
                    "Michael",
                    "Moby",
                    "Kim",
                ]
            ),
            age=random.randint(1, 50),
        )

        # create the message
        message = user.serialize()

        # publish
        channel.basic_publish(exchange="", routing_key=queue_name, body=message)


def main():
    rabbitmq_url = "amqp://guest:guest@localhost:5672/%2f"
    queue_name = "test-stream"
    params = pika.URLParameters(rabbitmq_url)

    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=True)

    produce(channel=channel, queue_name=queue_name)
    consume(channel=channel, queue_name=queue_name)

    connection.close()
