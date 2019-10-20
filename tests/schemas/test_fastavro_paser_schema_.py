import typing
import datetime
import uuid
import dataclasses

from fastavro import parse_schema

from dataclasses_avroschema.schema_generator import SchemaGenerator


def test_minimal_schema(user_dataclass):
    """
    Python class contains the primitive types:

    class User:
        name: str
        age: int
        has_pets: bool
        money: float
        encoded: bytes
    """
    schema = SchemaGenerator(user_dataclass).avro_schema_to_python()

    assert parse_schema(schema)


def test_schema_with_extra_avro_attrs(user_extra_avro_atributes_dataclass):
    """
    Python class contains the primitive types plus aliases and namespace

    class UserAliasesNamespace:
        name: str
        age: int

        def extra_avro_attributes() -> typing.Dict[str, typing.Any]:
            return {
                "namespace": "test.com.ar/user/v1",
                "aliases": ["User", "My favorite User"]
            }
    """
    schema = SchemaGenerator(user_extra_avro_atributes_dataclass).avro_schema_to_python()

    assert parse_schema(schema)


def test_advance_schema(user_advance_dataclass):
    """
    Python class contains the primitive, primitive with default values
    array, enum, map types.

    class UserAdvance:
        name: str
        age: int
        pets: typing.List[str]
        accounts: typing.Dict[str, int]
        has_car: bool = False
        favorite_colors: typing.Tuple[str] = ("BLUE", "YELLOW", "GREEN")
        country: str = "Argentina"
        address: str = None
    """
    schema = SchemaGenerator(user_advance_dataclass).avro_schema_to_python()

    assert parse_schema(schema)


def test_advance_schema_with_defaults(user_advance_with_defaults_dataclass):
    """
    Python class contains the primitive, primitive with default values
    array, enum, map types.

    class UserAdvance:
        name: str
        age: int
        pets: typing.List[str] = dataclasses.field(default_factory=lambda: ['dog', 'cat'])
        accounts: typing.Dict[str, int] = dataclasses.field(default_factory=lambda: {"key": 1})
        has_car: bool = False
        favorite_colors: typing.Tuple[str] = ("BLUE", "YELLOW", "GREEN")
        country: str = "Argentina"
        address: str = None
    """
    schema = SchemaGenerator(user_advance_with_defaults_dataclass)

    assert parse_schema(schema.avro_schema_to_python())


def test_one_to_one_schema():
    """
    Test relationship one-to-one
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

    assert parse_schema(SchemaGenerator(User).avro_schema_to_python())


def test_one_to_many_schema():
    """
    Test relationship one-to-many
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

    assert parse_schema(SchemaGenerator(User).avro_schema_to_python())


def test_one_to_many_with_map_schema():
    """
    Test relationship one-to-many using a map
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

    assert parse_schema(SchemaGenerator(User).avro_schema_to_python())


def test_one_to_one_self_relationship():
    """
    Test self relationship one-to-one
    """

    class User:
        "User with self reference as friend"
        name: str
        age: int
        friend: typing.Type["User"]

    assert parse_schema(SchemaGenerator(User).avro_schema_to_python())


def test_one_to_many_self_reference_schema():
    """
    Test self relationship one-to-many using an array
    """

    class User:
        "User with self reference as friends"
        name: str
        age: int
        friends: typing.List[typing.Type["User"]]

    assert parse_schema(SchemaGenerator(User).avro_schema_to_python())


def test_one_to_many_self_reference_map_schema():
    """
    Test self relationship one-to-many using a map
    """

    class User:
        "User with self reference as friends"
        name: str
        age: int
        friends: typing.Dict[str, typing.Type["User"]]

    assert parse_schema(SchemaGenerator(User).avro_schema_to_python())


def test_logical_types_schema():
    """
    Test a schema with Logical Types
    """
    a_datetime = datetime.datetime(2019, 10, 12, 17, 57, 42, 179133)

    class LogicalTypes:
        "Some logical types"
        birthday: datetime.date = a_datetime
        meeting_time: datetime.time = a_datetime
        release_datetime: datetime.datetime = a_datetime
        event_uuid: uuid.uuid4 = '09f00184-7721-4266-a955-21048a5cc235'

    assert parse_schema(SchemaGenerator(LogicalTypes).avro_schema_to_python())


def test_schema_with_union_types():
    class Bus:
        "A Bus"
        engine_name: str

    class Car:
        "A Car"
        engine_name: str

    class UnionSchema:
        "Some Unions"
        mountain_trip: typing.Union[Bus, Car] = dataclasses.field(
            default_factory=lambda: {"engine_name": "honda"})

    assert parse_schema(SchemaGenerator(UnionSchema).avro_schema_to_python())
