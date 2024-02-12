import dataclasses
import datetime
import enum
import json
import sys
import typing
import uuid

import pytest
from fastavro import parse_schema

from dataclasses_avroschema import AvroModel
from dataclasses_avroschema.types import JsonDict

PY_VER = sys.version_info


def test_schema_with_complex_types(user_advance_dataclass, user_advance_avro_json):
    assert user_advance_dataclass.avro_schema() == json.dumps(user_advance_avro_json)


def test_schema_with_complex_types_and_defaults(
    user_advance_with_defaults_dataclass, user_advance_with_defaults_avro_json
):
    assert user_advance_with_defaults_dataclass.avro_schema() == json.dumps(user_advance_with_defaults_avro_json)


def test_schema_with_unions_type(union_type_schema: JsonDict) -> None:
    @dataclasses.dataclass
    class Bus(AvroModel):
        "A Bus"

        engine_name: str

        class Meta:
            namespace = "types.bus_type"

    @dataclasses.dataclass
    class Car(AvroModel):
        "A Car"

        engine_name: str

        class Meta:
            namespace = "types.car_type"

    class TripDistance(enum.Enum):
        CLOSE = "Close"
        FAR = "Far"

        class Meta:
            doc = "Distance of the trip"
            namespace = "trip"

    @dataclasses.dataclass
    class UnionSchema(AvroModel):
        "Some Unions"

        first_union: typing.Union[str, int]
        logical_union: typing.Union[datetime.datetime, datetime.date, uuid.uuid4]
        lake_trip: typing.Union[Bus, Car]
        river_trip: typing.Optional[typing.Union[Bus, Car]] = None
        mountain_trip: typing.Union[Bus, Car] = dataclasses.field(default_factory=lambda: Bus(engine_name="honda"))
        trip_distance: typing.Optional[typing.Union[int, TripDistance]] = None
        optional_distance: typing.Optional[TripDistance] = None

    assert parse_schema(UnionSchema.avro_schema_to_python())
    assert UnionSchema.avro_schema() == json.dumps(union_type_schema)


# The following two tests were written for Issue 85 - Union field with default generating out-of-spec schema
# This test is written explicitly to adhere to the Avro spec. The general behavior is covered in other tests,
#   but the schemas generated are out-of-spec currently
def test_schema_with_unions_defaults(default_union_schema: JsonDict) -> None:
    class UserType(enum.Enum):
        BASIC = "Basic"
        PREMIUM = "Premium"

        class Meta:
            doc = "Type of user"

    @dataclasses.dataclass
    class User(AvroModel):
        "An User"

        name: str
        age: int
        user_type: typing.Optional[UserType] = None
        school_name: typing.Optional[str] = None
        school_id: typing.Union[int, str] = ""

    assert User.avro_schema() == json.dumps(default_union_schema)


# The following two tests were written for Issue 390 - Optional enum type
# with default value of enum - generated duplicate field definitions
# The problem is in the fact that first field occurrence for Enum is its full definition (dict)
# while further occurences are just the type name - which can cause problems when comparing lists of fields.


def test_schema_with_optional_enum_defaults(
    optional_enum_with_default_schema: JsonDict,
) -> None:
    class LimitTypes(enum.Enum):
        MIN_LIMIT = "MIN_LIMIT"
        MAX_LIMIT = "MAX_LIMIT"
        EXACT_LIMIT = "EXACT_LIMIT"

    @dataclasses.dataclass
    class LimitTest(AvroModel):
        limit_type: typing.Optional[LimitTypes] = LimitTypes.MIN_LIMIT

    assert LimitTest.avro_schema() == json.dumps(optional_enum_with_default_schema)


@pytest.mark.skipif(condition=PY_VER < (3, 10), reason="Union with syntax | is only for python >= 3.10")
def test_schema_with_new_unions_type_syntax(union_type_schema: JsonDict) -> None:
    @dataclasses.dataclass
    class Bus(AvroModel):
        "A Bus"

        engine_name: str

        class Meta:
            namespace = "types.bus_type"

    @dataclasses.dataclass
    class Car(AvroModel):
        "A Car"

        engine_name: str

        class Meta:
            namespace = "types.car_type"

    class TripDistance(enum.Enum):
        CLOSE = "Close"
        FAR = "Far"

        class Meta:
            doc = "Distance of the trip"
            namespace = "trip"

    @dataclasses.dataclass
    class UnionSchema(AvroModel):
        "Some Unions"

        first_union: str | int
        logical_union: datetime.datetime | datetime.date | uuid.UUID
        lake_trip: Bus | Car
        river_trip: Bus | Car | None = None
        mountain_trip: Bus | Car = dataclasses.field(default_factory=lambda: Bus(engine_name="honda"))  # type: ignore
        trip_distance: int | TripDistance | None = None
        optional_distance: TripDistance | None = None

    assert parse_schema(UnionSchema.avro_schema_to_python())
    assert UnionSchema.avro_schema() == json.dumps(union_type_schema)


# The following two tests were written for Issue 85 - Union field with default generating out-of-spec schema
# This test is written explicitly to adhere to the Avro spec. The general behavior is covered in other tests,
# but the schemas generated are out-of-spec currently
@pytest.mark.skipif(condition=PY_VER < (3, 10), reason="Union with syntax | is only for python >= 3.10")
def test_schema_with_new_unions_defaults_syntax(default_union_schema: JsonDict) -> None:
    class UserType(enum.Enum):
        BASIC = "Basic"
        PREMIUM = "Premium"

        class Meta:
            doc = "Type of user"

    @dataclasses.dataclass
    class User(AvroModel):
        "An User"

        name: str
        age: int
        user_type: UserType | None = None
        school_name: str | None = None
        school_id: int | str = ""

    assert User.avro_schema() == json.dumps(default_union_schema)


def test_repeated_enum_without_namespace() -> None:
    class UserType(enum.Enum):
        BASIC = "Basic"
        PREMIUM = "Premium"

    @dataclasses.dataclass
    class User(AvroModel):
        user_type: UserType
        user_type_optional: typing.Optional[UserType]

    parse_schema(User.avro_schema_to_python())


# This is to explicitly test the behavior for a typing.Optional[T] field with no default
# Current (as of 2020-11-19) is to generate a union [T, null], which is what this tests for
# This isn't out-of-spec, but does seem a little odd in accordance with defaults
# It means a typing.Optional[T] field can never have a default of None, and must be explicitly assigned None/null
def test_schema_typing_optional_behavior(typing_optional_schema: JsonDict) -> None:
    @dataclasses.dataclass
    class User(AvroModel):
        "An User"

        name: str
        age: int
        school_grade: typing.Optional[int]

    assert User.avro_schema() == json.dumps(typing_optional_schema)
