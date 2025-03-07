import enum
import random
from dataclasses import dataclass
from time import sleep
from typing import Optional

from kafka import KafkaConsumer, KafkaProducer

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


def consume():
    consumer = KafkaConsumer("my_topic", bootstrap_servers="localhost:9092", group_id="my-group")

    for msg in consumer:
        print(f"Message received: {msg.value} at {msg.timestamp}")

        user = UserModel.deserialize(msg.value)
        print(f"Message deserialized: {user}")

    print("Stoping consumer...")


def send(total_events=10):
    producer = KafkaProducer(bootstrap_servers="localhost:9092")

    for event_number in range(1, total_events + 1):
        # Produce message
        print(f"Sending event number {event_number}")

        # create an instance of User v1
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

        producer.send("my_topic", message)
        # sleep for 2 seconds
        sleep(1)

    print("Stoping producer...")


def main():
    send()
    consume()
