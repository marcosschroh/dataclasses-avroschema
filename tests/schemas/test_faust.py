import dataclasses
import datetime
import enum
import json
import typing
import uuid

import pytest
from faust.models import fields

from dataclasses_avroschema import types
from dataclasses_avroschema.faust import AvroRecord

encoded = "test".encode()


def test_faust_record_schema_primitive_types(user_avro_json):
    class User(AvroRecord):
        name: str
        age: int
        has_pets: bool
        money: float
        encoded: bytes

        class Meta:
            schema_doc = False

    assert User.avro_schema() == json.dumps(user_avro_json)


def test_faust_record_schema_complex_types(user_advance_avro_json, color_enum):
    class UserAdvance(AvroRecord):
        name: str
        age: int
        pets: typing.List[str]
        accounts: typing.Dict[str, int]
        favorite_colors: color_enum
        md5: types.confixed(size=16)
        has_car: bool = False
        country: str = "Argentina"
        address: typing.Optional[str] = None

        class Meta:
            schema_doc = False

    assert UserAdvance.avro_schema() == json.dumps(user_advance_avro_json)


def test_faust_record_schema_complex_types_with_defaults(user_advance_with_defaults_avro_json, color_enum):
    class UserAdvance(AvroRecord):
        name: str
        age: int
        pets: typing.List[str] = fields.StringField(required=False, default=["dog", "cat"])
        accounts: typing.Dict[str, int] = fields.IntegerField(required=False, default={"key": 1})
        has_car: bool = False
        favorite_colors: color_enum = color_enum.BLUE
        country: str = "Argentina"
        address: typing.Optional[str] = None

        class Meta:
            schema_doc = False

    assert UserAdvance.avro_schema() == json.dumps(user_advance_with_defaults_avro_json)


def test_faust_record_schema_logical_types(logical_types_schema):
    a_datetime = datetime.datetime(2019, 10, 12, 17, 57, 42, tzinfo=datetime.timezone.utc)
    delta = datetime.timedelta(weeks=1, days=2, hours=3, minutes=4, seconds=5, milliseconds=6, microseconds=7)

    class LogicalTypes(AvroRecord):
        "Some logical types"

        birthday: datetime.date = a_datetime.date()
        meeting_time: datetime.time = a_datetime.time()
        release_datetime: datetime.datetime = a_datetime
        time_elapsed: datetime.timedelta = delta
        event_uuid: uuid.uuid4 = "09f00184-7721-4266-a955-21048a5cc235"

    assert LogicalTypes.avro_schema() == json.dumps(logical_types_schema)


def test_faust_record_one_to_one_relationship(user_one_address_schema):
    """
    Test schema relationship one-to-one
    """

    class Address(AvroRecord):
        "An Address"

        street: str
        street_number: int

    class User(AvroRecord):
        "An User with Address"

        name: str
        age: int
        address: Address

    assert User.avro_schema() == json.dumps(user_one_address_schema)


def test_faust_record_one_to_one_relationship_with_none_default(
    user_one_address_schema_with_none_default,
):
    """
    Test schema relationship one-to-one
    """

    class Address(AvroRecord):
        "An Address"

        street: str
        street_number: int

    class User(AvroRecord):
        "An User with Address"

        name: str
        age: int
        address: typing.Optional[Address] = None

    assert User.avro_schema() == json.dumps(user_one_address_schema_with_none_default)


def test_faust_record_one_to_many_relationship(user_many_address_schema):
    """
    Test schema relationship one-to-many
    """

    class Address(AvroRecord):
        "An Address"

        street: str
        street_number: int

    class User(AvroRecord):
        "User with multiple Address"

        name: str
        age: int
        addresses: typing.List[Address]

    assert User.avro_schema() == json.dumps(user_many_address_schema)


def test_faust_record_one_to_many_map_relationship(user_many_address_map_schema):
    """
    Test schema relationship one-to-many using a map
    """

    class Address(AvroRecord):
        "An Address"

        street: str
        street_number: int

    class User(AvroRecord):
        "User with multiple Address"

        name: str
        age: int
        addresses: typing.Dict[str, Address]

    assert User.avro_schema() == json.dumps(user_many_address_map_schema)


def test_faust_record_self_one_to_one_relationship(
    user_self_reference_one_to_one_schema,
):
    """
    Test self relationship one-to-one
    """

    class User(AvroRecord):
        "User with self reference as friend"

        name: str
        age: int
        friend: typing.Type["User"]
        teamates: typing.Optional[typing.Type["User"]] = None

    assert User.avro_schema() == json.dumps(user_self_reference_one_to_one_schema)


def test_faust_record_self_one_to_many_relationship(
    user_self_reference_one_to_many_schema,
):
    """
    Test self relationship one-to-many
    """

    class User(AvroRecord):
        "User with self reference as friends"

        name: str
        age: int
        friends: typing.List[typing.Type["User"]]
        teamates: typing.List[typing.Type["User"]] = None

    assert User.avro_schema() == json.dumps(user_self_reference_one_to_many_schema)


def test_faust_record_self_one_to_many_map_relationship(
    user_self_reference_one_to_many_map_schema,
):
    """
    Test self relationship one-to-many Map
    """

    class User(AvroRecord):
        "User with self reference as friends"

        name: str
        age: int
        friends: typing.Dict[str, typing.Type["User"]]
        teamates: typing.Dict[str, typing.Type["User"]] = None

    assert User.avro_schema() == json.dumps(user_self_reference_one_to_many_map_schema)


@pytest.mark.skip(reason="skiping conflict with new faust-streaming version")
def test_faust_record_schema_with_unions_type(union_type_schema):
    class Bus(AvroRecord):
        "A Bus"

        engine_name: str

        class Meta:
            namespace = "types.bus_type"

    class Car(AvroRecord):
        "A Car"

        engine_name: str

        class Meta:
            namespace = "types.car_type"

    class TripDistance(enum.Enum):
        CLOSE = "Close"
        FAR = "Far"

        class Meta:
            doc = "Distance of the trip"

    class UnionSchema(AvroRecord):
        "Some Unions"

        first_union: typing.Union[str, int]
        logical_union: typing.Union[datetime.datetime, datetime.date, uuid.uuid4]
        lake_trip: typing.Union[Bus, Car]
        river_trip: typing.Union[None, Bus, Car] = None
        mountain_trip: typing.Union[Bus, Car] = dataclasses.field(default_factory=lambda: {"engine_name": "honda"})
        trip_distance: typing.Union[None, int, TripDistance] = None

    assert UnionSchema.avro_schema() == json.dumps(union_type_schema)


def test_field_metadata() -> None:
    field_matadata = {"aliases": ["username"]}

    class UserRecord(AvroRecord):
        name: str = dataclasses.field(metadata=field_matadata)

    schema = UserRecord.avro_schema_to_python()

    assert schema["fields"][0]["aliases"] == field_matadata["aliases"]


def test_exclude_field_from_schema(user_extra_avro_attributes):
    class User(AvroRecord):
        "An User"

        name: str
        age: int
        last_name: fields.StringField = fields.StringField(required=False, defualt="Bond")

        class Meta:
            namespace = "test.com.ar/user/v1"
            aliases = [
                "User",
                "My favorite User",
            ]
            exclude = [
                "last_name",
            ]

    assert User.avro_schema() == json.dumps(user_extra_avro_attributes)


def test_validate():
    class User(AvroRecord):
        name: str
        age: int
        has_pets: bool = True

    user = User(name="batman", age=20)
    assert user.validate() == []
    assert user.validate_avro()
