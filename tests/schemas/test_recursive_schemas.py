import json
import typing

from dataclasses_avroschema import AvroModel


def test_self_one_to_one_relationship(user_self_reference_one_to_one_schema):
    """
    Test self relationship one-to-one
    """

    class User(AvroModel):
        "User with self reference as friend"

        name: str
        age: int
        friend: typing.Type["User"]
        teamates: typing.Type["User"] = None

    assert User.avro_schema() == json.dumps(user_self_reference_one_to_one_schema)


def test_self_one_to_many_relationship(user_self_reference_one_to_many_schema):
    """
    Test self relationship one-to-many
    """

    class User(AvroModel):
        "User with self reference as friends"

        name: str
        age: int
        friends: typing.List[typing.Type["User"]]
        teamates: typing.List[typing.Type["User"]] = None

    assert User.avro_schema() == json.dumps(user_self_reference_one_to_many_schema)


def test_self_one_to_many_map_relationship(user_self_reference_one_to_many_map_schema):
    """
    Test self relationship one-to-many Map
    """

    class User(AvroModel):
        "User with self reference as friends"

        name: str
        age: int
        friends: typing.Dict[str, typing.Type["User"]]
        teamates: typing.Dict[str, typing.Type["User"]] = None

    assert User.avro_schema() == json.dumps(user_self_reference_one_to_many_map_schema)
