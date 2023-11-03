import datetime
import decimal
import typing
import uuid

import pydantic
import pytest

from dataclasses_avroschema import types
from dataclasses_avroschema.pydantic import AvroBaseModel

from .const import pydantic_fields as pydantic_fields


def test_fake_with_logical_types() -> None:
    class LogicalTypes(AvroBaseModel):
        birthday: datetime.date
        meeting_time: datetime.time
        meeting_time_micro: types.TimeMicro
        release_datetime: datetime.datetime
        release_datetime_micro: types.DateTimeMicro
        event_uuid: uuid.UUID

    assert isinstance(LogicalTypes.fake(), LogicalTypes)


def test_fake_union() -> None:
    class Bus(AvroBaseModel):
        engine_name: str

        class Meta:
            namespace = "types.bus_type"

    class Car(AvroBaseModel):
        engine_name: str

        class Meta:
            namespace = "types.car_type"

    class UnionSchema(AvroBaseModel):
        first_union: typing.Union[str, int]
        logical_union: typing.Union[datetime.datetime, datetime.date, uuid.UUID]
        lake_trip: typing.Union[Bus, Car]
        river_trip: typing.Optional[typing.Union[Bus, Car]] = None
        mountain_trip: typing.Union[Bus, Car] = pydantic.Field(default_factory=lambda: Bus(engine_name="honda"))

    assert isinstance(UnionSchema.fake(), UnionSchema)


def test_fake_one_to_one_relationship() -> None:
    """
    Test schema relationship one-to-one
    """

    class Address(AvroBaseModel):
        street: str
        street_number: int

    class User(AvroBaseModel):
        name: str
        age: int
        address: Address

    assert isinstance(User.fake(), User)


def test_fake_one_to_many_relationship() -> None:
    """
    Test schema relationship one-to-many
    """

    class Address(AvroBaseModel):
        street: str
        street_number: int

    class User(AvroBaseModel):
        name: str
        age: int
        addresses: typing.List[Address]

    user = User.fake()
    assert isinstance(user, User)
    assert User.avro_schema()


def test_fake_one_to_many_with_tuples() -> None:
    """
    Test schema relationship one-to-many
    """

    class Address(AvroBaseModel):
        street: str
        street_number: int

    class User(AvroBaseModel):
        addresses: typing.Tuple[Address, ...]

    user = User.fake()
    assert isinstance(user, User)
    assert User.avro_schema()
    assert isinstance(user.addresses, tuple)


def test_fake_one_to_many_map_relationship() -> None:
    """
    Test schema relationship one-to-many using a map
    """

    class Address(AvroBaseModel):
        street: str
        street_number: int

    class User(AvroBaseModel):
        name: str
        age: int
        addresses: typing.Dict[str, Address]

    assert isinstance(User.fake(), User)


def test_self_one_to_one_relationship() -> None:
    """
    Test self relationship one-to-one
    """

    class User(AvroBaseModel):
        name: str
        age: int
        teamates: typing.Optional["User"] = None

    assert isinstance(User.fake(), User)


def test_self_one_to_many_relationship() -> None:
    """
    Test self relationship one-to-many
    """

    class User(AvroBaseModel):
        name: str
        age: int
        points: typing.List[typing.Optional[types.Float32]]
        teamates: typing.Optional[typing.List["User"]] = None

    assert isinstance(User.fake(), User)


def test_self_one_to_many_map_relationship() -> None:
    """
    Test self relationship one-to-many Map
    """

    class User(AvroBaseModel):
        name: str
        age: int
        friends: typing.Optional[typing.Dict[str, "User"]] = None
        teamates: typing.Optional[typing.Dict[str, "User"]] = None

    assert isinstance(User.fake(), User)


def test_optional_relationship() -> None:
    class Address(AvroBaseModel):
        street: str
        street_number: int

    class User(AvroBaseModel):
        name: str
        age: int
        address: typing.Optional[Address] = None

    assert isinstance(User.fake(), User)


def test_decimals() -> None:
    """
    Test Decimal logical types
    """

    class User(AvroBaseModel):
        name: str
        age: int
        test_score_1: types.condecimal(max_digits=11, decimal_places=5)
        test_score_2: types.condecimal(max_digits=5, decimal_places=2) = decimal.Decimal("100.00")

    assert isinstance(User.fake(), User)


def test_int32() -> None:
    """
    Test Int32 type
    """

    class User(AvroBaseModel):
        name: str
        age: int
        test_score_1: types.Int32 = 100
        test_score_2: types.Int32 = types.Int32(12)

    assert isinstance(User.fake(), User)


def test_float32() -> None:
    """
    Test Float32 type
    """

    class User(AvroBaseModel):
        name: str
        age: int
        test_score_1: types.Float32 = 100.0
        test_score_2: types.Float32 = types.Float32(12.4)

    assert isinstance(User.fake(), User)


@pytest.mark.parametrize("pydantic_field", pydantic_fields)
def test_pydantic_field(pydantic_field) -> None:
    class User(AvroBaseModel):
        name: pydantic_field

    assert isinstance(User.fake(), User)
