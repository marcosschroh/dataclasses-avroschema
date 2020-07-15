import dataclasses
import typing

from dataclasses_avroschema import AvroModel


def test_self_one_to_one_relationship():
    """
    Test self relationship one-to-one serialization
    """

    @dataclasses.dataclass
    class User(AvroModel):
        "User with self reference as friend"
        name: str
        age: int
        friend: typing.Type["User"] = None

    data_friend = {
        "name": "john",
        "age": 20,
    }

    friend = User(**data_friend)

    data_user = {
        "name": "juan",
        "age": 20,
        "friend": friend,
    }

    user = User(**data_user)

    avro_binary = b"\x08juan(\x02\x08john(\x00"
    # Seems a bug in fastavro
    # avro_json_binary = b'{"name": "juan", "age": 20, "friend": {"name": "john", "age": 20, "friend": None}}'
    expected = {
        "name": "juan",
        "age": 20,
        "friend": {"name": "john", "age": 20, "friend": None},
    }

    assert user.serialize() == avro_binary
    # assert user.serialize(serialization_type="avro-json") == avro_json_binary
    assert User.deserialize(avro_binary) == expected
    # Seems a bug in fastavro
    # assert User.deserialize(avro_json_binary, serialization_type="avro-json") == expected

    assert user.to_json() == expected


def test_self_one_to_many_relationship():
    """
    Test self relationship one-to-many serialization
    """

    @dataclasses.dataclass
    class User(AvroModel):
        "User with self reference as friends"
        name: str
        age: int
        friends: typing.List[typing.Type["User"]] = None

    data_friend = {"name": "john", "age": 20, "friends": None}
    friend = User(**data_friend)

    data_user = {
        "name": "juan",
        "age": 20,
        "friends": [friend],
    }
    user = User(**data_user)

    # Bug in fastavro. Check adding the namespace
    # Can not calculate the binary

    expected = {
        "name": "juan",
        "age": 20,
        "friends": [data_friend],
    }
    assert user.to_json() == expected


def test_self_one_to_many_map_relationship():
    """
    Test self relationship one-to-many Map serialization
    """

    @dataclasses.dataclass
    class User(AvroModel):
        "User with self reference as friends"
        name: str
        age: int
        friends: typing.Dict[str, typing.Type["User"]] = None

    data_friend = {
        "name": "john",
        "age": 20,
        "friends": None,
    }
    friend = User(**data_friend)

    data_user = {
        "name": "juan",
        "age": 20,
        "friends": {"a_friend": friend},
    }
    user = User(**data_user)

    # Bug in fastavro. Check adding the namespace
    # Can not calculate the binary

    expected = {
        "name": "juan",
        "age": 20,
        "friends": {"a_friend": data_friend},
    }
    assert user.to_json() == expected
