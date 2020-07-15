import dataclasses
import typing

from dataclasses_avroschema import AvroModel


def test_one_to_one_relationship():
    """
    Test schema relationship one-to-one serialization
    """

    @dataclasses.dataclass
    class Address(AvroModel):
        "An Address"
        street: str
        street_number: int

    @dataclasses.dataclass
    class User(AvroModel):
        "An User with Address"
        name: str
        age: int
        address: Address

    address_data = {
        "street": "test",
        "street_number": 10,
    }

    address = Address(**address_data)

    data_user = {
        "name": "john",
        "age": 20,
        "address": address,
    }

    user = User(**data_user)

    avro_binary = b"\x08john(\x08test\x14"
    avro_json_binary = b'{"name": "john", "age": 20, "address": {"street": "test", "street_number": 10}}'
    expected = {"name": "john", "age": 20, "address": {"street": "test", "street_number": 10}}

    assert user.serialize() == avro_binary
    assert user.serialize(serialization_type="avro-json") == avro_json_binary
    assert User.deserialize(avro_binary) == expected
    assert User.deserialize(avro_json_binary, serialization_type="avro-json") == expected

    assert user.to_json() == expected


def test_one_to_many_relationship():
    """
    Test schema relationship one-to-many serialization
    """

    @dataclasses.dataclass
    class Address(AvroModel):
        "An Address"
        street: str
        street_number: int

    @dataclasses.dataclass
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

    user = User(**data_user)

    avro_binary = b"\x08john(\x02\x08test\x14\x00"
    avro_json_binary = b'{"name": "john", "age": 20, "addresses": [{"street": "test", "street_number": 10}]}'
    expected = {"name": "john", "age": 20, "addresses": [{"street": "test", "street_number": 10}]}

    assert user.serialize() == avro_binary
    assert user.serialize(serialization_type="avro-json") == avro_json_binary
    assert User.deserialize(avro_binary) == expected
    assert User.deserialize(avro_json_binary, serialization_type="avro-json") == expected

    assert user.to_json() == expected


def test_one_to_many_map_relationship():
    """
    Test schema relationship one-to-many using a map serialization
    """

    @dataclasses.dataclass
    class Address(AvroModel):
        "An Address"
        street: str
        street_number: int

    @dataclasses.dataclass
    class User(AvroModel):
        "User with multiple Address"
        name: str
        age: int
        addresses: typing.Dict[str, Address]

    address_data = {
        "street": "test",
        "street_number": 10,
    }

    address = Address(**address_data)

    data_user = {
        "name": "john",
        "age": 20,
        "addresses": {"main_residence": address},
    }

    user = User(**data_user)

    avro_binary = b"\x08john(\x02\x1cmain_residence\x08test\x14\x00"
    avro_json_binary = (
        b'{"name": "john", "age": 20, "addresses": {"main_residence": {"street": "test", "street_number": 10}}}'
    )
    expected = {"name": "john", "age": 20, "addresses": {"main_residence": {"street": "test", "street_number": 10}}}

    assert user.serialize() == avro_binary
    assert user.serialize(serialization_type="avro-json") == avro_json_binary
    assert User.deserialize(avro_binary) == expected

    # seems that there is a bug in fastavro and raises KeyError
    # assert User.deserialize(avro_json_binary, serialization_type="avro-json") == expected

    assert user.to_json() == expected
