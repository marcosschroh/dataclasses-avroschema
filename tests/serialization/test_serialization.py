import typing
from dataclasses import dataclass

import pytest

from dataclasses_avroschema import AvroModel


def create_user():
    @dataclass
    class Address(AvroModel):
        "An Address"
        street: str
        street_number: int

    @dataclass
    class User(AvroModel):
        "User with multiple Address"
        name: str
        age: int
        addresses: typing.List[Address]

    address_data = {
        "street": "test",
        "street_number": 10,
    }

    address = Address(**address_data)

    data_user = {
        "name": "john",
        "age": 20,
        "addresses": [address],
    }

    return User(**data_user)


def test_serialization():
    avro_binary = b"\x08john(\x02\x08test\x14\x00"
    avro_json_binary = b'{"name": "john", "age": 20, "addresses": [{"street": "test", "street_number": 10}]}'
    user = create_user()

    assert user.serialize() == avro_binary

    assert user.serialize(serialization_type="avro-json") == avro_json_binary


def test_deserialization():
    avro_binary = b"\x08john(\x02\x08test\x14\x00"
    avro_json_binary = b'{"name": "john", "age": 20, "addresses": [{"street": "test", "street_number": 10}]}'
    expected = {"name": "john", "age": 20, "addresses": [{"street": "test", "street_number": 10}]}
    user = create_user()

    assert user.deserialize(avro_binary) == expected
    assert user.deserialize(avro_json_binary, serialization_type="avro-json") == expected


def test_deserialization_with_class():
    class Address(AvroModel):
        "An Address"
        street: str
        street_number: int

    class User(AvroModel):
        "User with multiple Address"
        name: str
        age: int
        addresses: typing.List[Address]

    avro_binary = b"\x08john(\x02\x08test\x14\x00"
    avro_json_binary = b'{"name": "john", "age": 20, "addresses": [{"street": "test", "street_number": 10}]}'
    expected = {"name": "john", "age": 20, "addresses": [{"street": "test", "street_number": 10}]}

    assert User.deserialize(avro_binary) == expected
    assert User.deserialize(avro_json_binary, serialization_type="avro-json") == expected


def test_invalid_serialization_deserialization_types():
    user = create_user()

    with pytest.raises(ValueError):
        user.serialize(serialization_type="json")

    with pytest.raises(ValueError):
        user.deserialize(b"", serialization_type="json")


def test_to_json():
    user = create_user()
    payload = {"name": "john", "age": 20, "addresses": [{"street": "test", "street_number": 10}]}

    assert user.to_json() == payload
