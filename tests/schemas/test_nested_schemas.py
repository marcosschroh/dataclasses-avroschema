import json
import typing

from dataclasses_avroschema import AvroModel


def test_one_to_one_relationship(user_one_address_schema):
    """
    Test schema relationship one-to-one
    """

    class Address(AvroModel):
        "An Address"
        street: str
        street_number: int

    class User(AvroModel):
        "An User with Address"
        name: str
        age: int
        address: Address

    assert User.avro_schema() == json.dumps(user_one_address_schema)


def test_one_to_many_relationship(user_many_address_schema):
    """
    Test schema relationship one-to-many
    """

    class Address(AvroModel):
        "An Address"
        street: str
        street_number: int

    class User(AvroModel):
        "User with multiple Address"
        name: str
        age: int
        addresses: typing.List[Address]

    assert User.avro_schema() == json.dumps(user_many_address_schema)


def test_one_to_many_map_relationship(user_many_address_map_schema):
    """
    Test schema relationship one-to-many using a map
    """

    class Address(AvroModel):
        "An Address"
        street: str
        street_number: int

    class User(AvroModel):
        "User with multiple Address"
        name: str
        age: int
        addresses: typing.Dict[str, Address]

    assert User.avro_schema() == json.dumps(user_many_address_map_schema)


def test_one_to_many_map_relationship_with_alias(user_many_address_map_schema_alias_item):
    """
    Test schema relationship one-to-many using a map
    """

    class Address(AvroModel):
        "An Address"
        street: str
        street_number: int

    class User(AvroModel):
        "User with multiple Address"
        name: str
        age: int
        addresses: typing.Dict[str, Address]

        class Meta:
            alias_nested_items = {"address": "Address"}

    assert User.avro_schema() == json.dumps(user_many_address_map_schema_alias_item)


def test_alias_nested_item(user_one_address_alias_item):
    """
    Test schema relationship one-to-one
    """

    class Address(AvroModel):
        "An Address"
        street: str
        street_number: int

    class User(AvroModel):
        "An User with Address"
        name: str
        age: int
        address: Address

        class Meta:
            alias_nested_items = {"address": "Address"}

    assert User.avro_schema() == json.dumps(user_one_address_alias_item)


def test_alias_nested_item_with_array(user_array_address_alias):
    class Address(AvroModel):
        "An Address"
        street: str
        street_number: int

    class User(AvroModel):
        "An User with Address"
        name: str
        age: int
        address: typing.List[Address]  # default name Address

        class Meta:
            alias_nested_items = {"address": "MySuperAddress"}

    assert User.avro_schema() == json.dumps(user_array_address_alias)


def test_alias_nested_item_with_map(user_map_address_alias):
    class Address(AvroModel):
        "An Address"
        street: str
        street_number: int

    class User(AvroModel):
        "An User with Address"
        name: str
        age: int
        address: typing.Dict[str, Address]  # default name Address

        class Meta:
            alias_nested_items = {"address": "MySuperAddress"}

    assert User.avro_schema() == json.dumps(user_map_address_alias)
