from gearsclient import GearsRemoteBuilder as GearsBuilder

# import redis

from dataclasses import dataclass
import random
from time import sleep

from walrus import Database  # A subclass of the redis-py Redis client.

from dataclasses_avroschema import AvroModel, types


@dataclass
class UserModel(AvroModel):
    "An User"
    name: str
    age: int
    favorite_colors: types.Enum = types.Enum(["BLUE", "YELLOW", "GREEN"], default="BLUE")
    country: str = "Argentina"
    address: str = None
    testing: bool = False

    class Meta:
        namespace = "User.v1"
        aliases = ["user-v1", "super user"]


def consume(conn):
    result = GearsBuilder('StreamReader', r=conn).\
        map(lambda x:execute('hget', x, 'genres')).\
        filter(lambda x:x != '\\N').\
        flatmap(lambda x: x.split(',')).\
        map(lambda x: x.strip()).\
        countby().\
        run()

    print(result)


def produce(consumer_group):
    for i in range(10):
        # create an instance of User v1
        user = UserModel(
            name=random.choice(["Juan", "Peter", "Michael", "Moby", "Kim",]),
            age=random.randint(1, 50)
        )

        msgid = consumer_group.my_stream.add({"message": user.serialize()})
        print(f"Producing message {msgid}")

    print("Producer finished....")
    print("#" * 80)
    sleep(2)


if __name__ == "__main__":
    db = Database()
    stream_name = 'my-stream'
    db.Stream(stream_name)  # Create a new stream instance

    # create the consumer group
    consumer_group = db.consumer_group('my-consumer-group-1', [stream_name])
    consumer_group.create()  # Create the consumer group.
    consumer_group.set_id('$')

    produce(consumer_group)
    consume(db)
