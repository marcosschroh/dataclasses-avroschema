import json
import typing

from dataclasses_avroschema.schema_generator import SchemaGenerator


def test_one_to_one_relationship(user_one_address_schema):
    """
    Test schema relationship one-to-one
    """
    class Address:
        "An Address"
        street: str
        street_number: int

    class User:
        "An User with Address"
        name: str
        age: int
        address: Address

    schema = SchemaGenerator(User).avro_schema()
    assert schema == json.dumps(user_one_address_schema)


def test_one_to_many_relationship(user_many_address_schema):
    """
    Test schema relationship one-to-many
    """
    class Address:
        "An Address"
        street: str
        street_number: int

    class User:
        "User with multiple Address"
        name: str
        age: int
        addresses: typing.List[Address]

    schema = SchemaGenerator(User).avro_schema()
    assert schema == json.dumps(user_many_address_schema)


def test_one_to_many_map_relationship(user_many_map_address_schema):
    """
    Test schema relationship one-to-many using a map
    """
    class Address:
        "An Address"
        street: str
        street_number: int

    class User:
        "User with multiple Address"
        name: str
        age: int
        addresses: typing.Dict[str, Address]

    schema = SchemaGenerator(User).avro_schema()
    assert schema == json.dumps(user_many_map_address_schema)
