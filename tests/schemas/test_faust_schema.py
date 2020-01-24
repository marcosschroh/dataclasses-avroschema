import dataclasses
import datetime
import json
import typing
import uuid

import faust

from dataclasses_avroschema import schema_definition
from dataclasses_avroschema.schema_generator import SchemaGenerator

encoded = "test".encode()


def test_faust_record_schema_primitive_types(user_dataclass, user_avro_json):
    class User(faust.Record):
        name: str
        age: int
        has_pets: bool
        money: float
        encoded: bytes

    user_schema = SchemaGenerator(User, include_schema_doc=False).avro_schema()

    assert user_schema == json.dumps(user_avro_json)


def test_faust_record_schema_complex_types(user_advance_avro_json):
    class UserAdvance(faust.Record):
        name: str
        age: int
        pets: typing.List[str]
        accounts: typing.Dict[str, int]
        has_car: bool = False
        favorite_colors: typing.Tuple[str] = ("BLUE", "YELLOW", "GREEN")
        country: str = "Argentina"
        address: str = None

    user_schema = SchemaGenerator(UserAdvance, include_schema_doc=False).avro_schema()

    assert user_schema == json.dumps(user_advance_avro_json)


def test_faust_record_schema_complex_types_with_defaults(
    user_advance_with_defaults_avro_json
):
    class UserAdvance(faust.Record):
        name: str
        age: int
        pets: typing.List[str] = dataclasses.field(
            default_factory=lambda: ["dog", "cat"]
        )
        accounts: typing.Dict[str, int] = dataclasses.field(
            default_factory=lambda: {"key": 1}
        )
        has_car: bool = False
        favorite_colors: typing.Tuple[str] = ("BLUE", "YELLOW", "GREEN")
        country: str = "Argentina"
        address: str = None

    user_schema = SchemaGenerator(UserAdvance, include_schema_doc=False).avro_schema()

    assert user_schema == json.dumps(user_advance_with_defaults_avro_json)


def test_faust_record_schema_logical_types(logical_types_schema):
    a_datetime = datetime.datetime(2019, 10, 12, 17, 57, 42)

    class LogicalTypes(faust.Record):
        "Some logical types"
        birthday: datetime.date = a_datetime.date()
        meeting_time: datetime.time = a_datetime.time()
        release_datetime: datetime.datetime = a_datetime
        event_uuid: uuid.uuid4 = "09f00184-7721-4266-a955-21048a5cc235"

    schema = SchemaGenerator(LogicalTypes).avro_schema()

    assert schema == json.dumps(logical_types_schema)


def test_faust_record_one_to_one_relationship(user_one_address_schema):
    """
    Test schema relationship one-to-one
    """

    class Address(faust.Record):
        "An Address"
        street: str
        street_number: int

    class User(faust.Record):
        "An User with Address"
        name: str
        age: int
        address: Address

    schema = SchemaGenerator(User).avro_schema()
    assert schema == json.dumps(user_one_address_schema)


def test_faust_record_one_to_many_relationship(user_many_address_schema):
    """
    Test schema relationship one-to-many
    """

    class Address(faust.Record):
        "An Address"
        street: str
        street_number: int

    class User(faust.Record):
        "User with multiple Address"
        name: str
        age: int
        addresses: typing.List[Address]

    schema = SchemaGenerator(User).avro_schema()
    assert schema == json.dumps(user_many_address_schema)


def test_faust_record_one_to_many_map_relationship(user_many_address_map_schema):
    """
    Test schema relationship one-to-many using a map
    """

    class Address(faust.Record):
        "An Address"
        street: str
        street_number: int

    class User(faust.Record):
        "User with multiple Address"
        name: str
        age: int
        addresses: typing.Dict[str, Address]

    schema = SchemaGenerator(User).avro_schema()
    assert schema == json.dumps(user_many_address_map_schema)


def test_faust_record_self_one_to_one_relationship(
    user_self_reference_one_to_one_schema
):
    """
    Test self relationship one-to-one
    """

    class User(faust.Record):
        "User with self reference as friend"
        name: str
        age: int
        friend: typing.Type["User"]

    schema = SchemaGenerator(User).avro_schema()

    assert schema == json.dumps(user_self_reference_one_to_one_schema)


def test_faust_record_self_one_to_many_relationship(
    user_self_reference_one_to_many_schema
):
    """
    Test self relationship one-to-many
    """

    class User(faust.Record):
        "User with self reference as friends"
        name: str
        age: int
        friends: typing.List[typing.Type["User"]]

    schema = SchemaGenerator(User).avro_schema()

    assert schema == json.dumps(user_self_reference_one_to_many_schema)


def test_faust_record_self_one_to_many_map_relationship(
    user_self_reference_one_to_many_map_schema
):
    """
    Test self relationship one-to-many Map
    """

    class User(faust.Record):
        "User with self reference as friends"
        name: str
        age: int
        friends: typing.Dict[str, typing.Type["User"]]

    schema = SchemaGenerator(User).avro_schema()

    assert schema == json.dumps(user_self_reference_one_to_many_map_schema)


def test_faust_record_schema_with_unions_type(union_type_schema):
    class Bus(faust.Record):
        "A Bus"
        engine_name: str

    class Car(faust.Record):
        "A Car"
        engine_name: str

    class UnionSchema(faust.Record):
        "Some Unions"
        first_union: typing.Union[str, int]
        logical_union: typing.Union[datetime.datetime, datetime.date, uuid.uuid4]
        lake_trip: typing.Union[Bus, Car]
        river_trip: typing.Union[Bus, Car] = None
        mountain_trip: typing.Union[Bus, Car] = dataclasses.field(
            default_factory=lambda: {"engine_name": "honda"}
        )

    schema = SchemaGenerator(UnionSchema).avro_schema()
    assert schema == json.dumps(union_type_schema)


def test_faust_not_installed(monkeypatch, user_avro_json):
    monkeypatch.setattr(schema_definition, "faust", None)

    class User:
        name: str
        age: int
        has_pets: bool
        money: float
        encoded: bytes

    user_schema = SchemaGenerator(User, include_schema_doc=False).avro_schema()

    assert user_schema == json.dumps(user_avro_json)
