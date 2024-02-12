import enum
import json
import random
from dataclasses import dataclass
from time import sleep

from gearsclient import GearsRemoteBuilder as GearsBuilder
from walrus import Database  # A subclass of the redis-py Redis client.

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
    address: str = None
    testing: bool = False

    class Meta:
        namespace = "User.v1"
        aliases = ["user-v1", "super user"]


def consume(conn, stream_name):
    """
    Consume messages from Stream and filter the events by age >= 25
    """
    return (
        GearsBuilder("StreamReader", r=conn)
        .map(lambda x: (json.loads(x["value"]["message"])))
        .filter(lambda x: x["age"] >= 25)
        .run(stream_name)
    )


def produce(stream):
    for i in range(10):
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

        msgid = stream.add({"message": user.serialize(serialization_type="avro-json")})
        print(f"Producing message {msgid}")

    print("Producer finished....")
    print("#" * 80)
    sleep(2)


if __name__ == "__main__":
    db = Database()
    stream_name = "my_stream"
    stream = db.Stream(stream_name)  # Create a new stream instance

    produce(stream)
    results = consume(db, stream_name)

    print(results)
