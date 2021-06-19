import dataclasses
import datetime
import enum
import json
import typing
import uuid

from dataclasses_avroschema import AvroModel


def test_schema_with_complex_types(user_advance_dataclass, user_advance_avro_json):
    assert user_advance_dataclass.avro_schema() == json.dumps(user_advance_avro_json)


def test_schema_with_complex_types_and_defaults(
    user_advance_with_defaults_dataclass, user_advance_with_defaults_avro_json
):
    assert user_advance_with_defaults_dataclass.avro_schema() == json.dumps(user_advance_with_defaults_avro_json)


def test_schema_with_unions_type(union_type_schema):
    class Bus(AvroModel):
        "A Bus"
        engine_name: str

    class Car(AvroModel):
        "A Car"
        engine_name: str

    class TripDistance(enum.Enum):
        CLOSE = "Close"
        FAR = "Far"

        class Meta:
            doc = "Distance of the trip"

    class UnionSchema(AvroModel):
        "Some Unions"
        first_union: typing.Union[str, int]
        logical_union: typing.Union[datetime.datetime, datetime.date, uuid.uuid4]
        lake_trip: typing.Union[Bus, Car]
        river_trip: typing.Union[Bus, Car] = None
        mountain_trip: typing.Union[Bus, Car] = dataclasses.field(default_factory=lambda: {"engine_name": "honda"})
        trip_distance: typing.Union[int, TripDistance] = None

    assert UnionSchema.avro_schema() == json.dumps(union_type_schema)


# The following two tests were written for Issue 85 - Union field with default generating out-of-spec schema
# This test is written explicitly to adhere to the Avro spec. The general behavior is covered in other tests,
#   but the schemas generated are out-of-spec currently
def test_schema_with_unions_defaults(default_union_schema):
    class UserType(enum.Enum):
        BASIC = "Basic"
        PREMIUM = "Premium"

        class Meta:
            doc = "Type of user"

    class User(AvroModel):
        "An User"
        name: str
        age: int
        user_type: typing.Optional[UserType] = None
        school_name: typing.Optional[str] = None
        school_id: typing.Union[int, str] = ""

    assert User.avro_schema() == json.dumps(default_union_schema)


# This is to explicitly test the behavior for a typing.Optional[T] field with no default
# Current (as of 2020-11-19) is to generate a union [T, null], which is what this tests for
# This isn't out-of-spec, but does seem a little odd in accordance with defaults
# It means a typing.Optional[T] field can never have a default of None, and must be explicitly assigned None/null
def test_schema_typing_optional_behavior(typing_optional_schema):
    class User(AvroModel):
        "An User"
        name: str
        age: int
        school_grade: typing.Optional[int]

    assert User.avro_schema() == json.dumps(typing_optional_schema)
