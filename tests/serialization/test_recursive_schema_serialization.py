import dataclasses
import typing

import pytest

from dataclasses_avroschema import AvroModel, utils
from dataclasses_avroschema.faust import AvroRecord
from dataclasses_avroschema.pydantic import AvroBaseModel
from dataclasses_avroschema.pydantic.v1 import AvroBaseModel as AvroBaseModelV1


def get_parametrize():
    parametrize = [
        pytest.param(AvroModel, dataclasses.dataclass, id="AvroModel"),
        pytest.param(AvroBaseModel, lambda f: f, id="AvroBaseModel"),
        pytest.param(AvroRecord, dataclasses.dataclass, id="AvroRecord"),
    ]

    if not utils.is_python_314_or_newer():
        parametrize.append(pytest.param(AvroBaseModelV1, lambda f: f, id="AvroBaseModelV1"))
    return parametrize


parametrize_base_model = pytest.mark.parametrize(
    "model_class, decorator",
    get_parametrize(),
)


@parametrize_base_model
def test_self_one_to_one_relationship(model_class: typing.Type[AvroModel], decorator: typing.Callable):
    """
    Test self relationship one-to-one serialization
    """

    @decorator
    class User(model_class):
        "User with self reference as friend"

        name: str
        age: int
        friend: typing.Optional["User"] = None

    data_friend = {
        "name": "john",
        "age": 20,
        "friend": None,
    }

    friend = User.parse_obj(data_friend)

    data_user = {
        "name": "juan",
        "age": 20,
        "friend": friend,
    }

    user = User.parse_obj(data_user)

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

    assert User.deserialize(avro_binary, create_instance=False) == expected

    # TODO: Bug in typing or fastavro
    # assert User.deserialize(avro_binary) == user

    # Seems a bug in fastavro
    # assert User.deserialize(avro_json_binary, serialization_type="avro-json") == expected

    assert user.to_dict() == expected


# don't test AvroBaseModel due to typing incompatibilites with Pydantic
@pytest.mark.parametrize(
    "model_class, decorator",
    [
        (AvroModel, dataclasses.dataclass),
        (AvroRecord, lambda f: f),
    ],
)
def test_self_one_to_many_relationship(model_class: typing.Type[AvroModel], decorator: typing.Callable):
    """
    Test self relationship one-to-many serialization
    """

    @decorator
    class User(model_class):
        "User with self reference as friends"

        name: str
        age: int
        friends: typing.Optional[typing.List[typing.Type["User"]]] = None

    data_friend = {"name": "john", "age": 20, "friends": []}
    friend = User.parse_obj(data_friend)

    data_user = {
        "name": "juan",
        "age": 20,
        "friends": [friend],
    }
    user = User.parse_obj(data_user)

    expected = {
        "name": "juan",
        "age": 20,
        "friends": [data_friend],
    }

    avro_binary = b"\x08juan(\x02\x02\x08john(\x02\x00\x00"
    # avro_json = b'{"name": "juan", "age": 20, "friends": [{"name": "john", "age": 20, "friends": []}]}'

    assert user.serialize() == avro_binary

    # TODO: Bug in fastavro
    # assert user.serialize(serialization_type="avro-json") == avro_json_binary

    assert User.deserialize(avro_binary, create_instance=False) == expected

    # TODO: Bug in fastavro
    # assert User.deserialize(avro_json, create_instance=False, serialization_type="avro-json") == expected

    # TODO: Bug in dacite
    # assert User.deserialize(avro_binary) == user

    assert user.to_dict() == expected


@pytest.mark.parametrize(
    "model_class, decorator",
    [
        (AvroModel, dataclasses.dataclass),
        (AvroRecord, lambda f: f),
    ],
)
def test_self_one_to_many_map_relationship(model_class: typing.Type[AvroModel], decorator: typing.Callable):
    """
    Test self relationship one-to-many Map serialization
    """

    @decorator
    class User(model_class):
        "User with self reference as friends"

        name: str
        age: int
        friends: typing.Optional[typing.Dict[str, typing.Type["User"]]] = None

    data_friend = {
        "name": "john",
        "age": 20,
        "friends": {},
    }
    friend = User.parse_obj(data_friend)

    data_user = {
        "name": "juan",
        "age": 20,
        "friends": {"a_friend": friend},
    }
    user = User.parse_obj(data_user)

    avro_binary = b"\x08juan(\x02\x02\x10a_friend\x08john(\x02\x00\x00"
    # avro_json = b'{"name": "juan", "age": 20, "friends": {"a_friend": {"name": "john", "age": 20, "friends": {}}}}'

    expected = {
        "name": "juan",
        "age": 20,
        "friends": {"a_friend": data_friend},
    }

    assert user.serialize() == avro_binary
    # TODO: Bug in fastavro
    # assert user.serialize(serialization_type="avro-json") == avro_json_binary

    assert User.deserialize(avro_binary, create_instance=False) == expected

    # TODO: Bug in fastavro
    # assert User.deserialize(avro_json, create_instance=False, serialization_type="avro-json") == expected

    # TODO: Bug in dacite
    # assert User.deserialize(avro_binary) == user
    assert user.to_dict() == expected
